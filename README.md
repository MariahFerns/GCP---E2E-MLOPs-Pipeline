# ML-OPS CI/CD Pipeline with GCP

This guide will help you set up a CI/CD pipeline for your ML models using Google Cloud Platform (GCP). This pipeline will enable continuous integration and deployment (CI/CD) with Vertex AI, Cloud Build, and GitHub.

## Prerequisites

1. A **Google Cloud Platform** account 
- **(Note: This setup requires a paid GCP account to complete the training pipeline till deployment however you can get till automatically generating triggers and creating the pipeline on a trial billing account)**.
2. **GitHub Repository** for your code.

## Setup Steps

### 1. Enable Required APIs

1. Go to the **APIs & Services** section in your GCP console and enable the following APIs if not enabled already:
   - Vertex AI API
   - Cloud Build API
   - Container Registry API

    *throughout the tutorial you may be prompted to enable additional apis so enable them to proceed further*
    
   ![Enable APIs in GCP](https://drive.google.com/uc?export=view&id=1Wlwmh6PVSTUkAC7NzeVb1nxLDHqguZvU) 

### 2. Set Up Cloud Build

1. In **IAM & Admin** create a new service account which will handle the Cloud Build builds.
   - IAM → Service Accounts → Create Service Account
   -- Give it a Name
   -- In step 2 Select a role and give it the `Cloud Build Service Account`
   [Role Selection](https://drive.google.com.uc?export=view&id=1DQs7RdZY5zqLmnMyEBrM0u-HFvFF-voI)
   -- Click done

2. In **Cloud Build**, create a **Host Connection** with your **GitHub Repository**.
   - Go to Cloud Build → Repositories → Create Host Connection and connect your GitHub account (You may be prompted to enable the secret manager api).
   
   ![Host Connection GitHub to Cloud Build](https://drive.google.com/uc?export=view&id=1bTe4QTrt7Gb2VW9wdzRVDXvyu5PAkgC0)
   
   - Once a host connection is made connect the repository in which your code is hosted by clicking link repository

   ![Connect Repository](https://drive.google.com/uc?export=view&id=1P5SKmdeuH88EliSVZiO5__S0PFPp1GYX) 

   -If you've correctly configured the above it should look like this

   ![Configured Connection and Repository](https://drive.google.com/uc?export=view&id=1BOm3Pbyf7OoPImZmFKXxx8PwJb5813WY)

3. Select the repository where your code is hosted and create a trigger for commits pushed to the `main` branch:
   
   **Cloud Build → Triggers → Create Trigger**
   - Event : Push to a branch
   - Source: `2nd gen` - this will be whichever generation you had linked your repository in.
   - Branch: `main`
   - Configuration Type: `Cloud Build configuration file (yaml or json)`
   - location: Repository → `cloudbuild.yaml`

   ![Create Cloud Build Trigger](https://drive.google.com/uc?export=view&id=1p_sT6kYJJA8aKWc21Kd7L8tqoNj-_P27) 

   - After configuring all these you will have to select the service account you want to link to the trigger; Select the service account we configured earlier and click create.
   
   ![Trigger Created](https://drive.google.com.uc?export=view&id=1uOwTaDU_CjmtHisr5uin1Q7SkdEVgWVt)

### 3. Configure Docker Repository in GCR

1. Create a **Google Container Registry (GCR)** repository to store your Docker images:
   Go to **Container Registry** → Create Repository 
   - Give a name to the repo and save this name to update REPO_NAME later
   - format: `Docker`
   - region: `us-central1` *any according to your project*
   - Leave everything else default and create the container repository.

2. Update the `cloudbuild.yaml` file in your GitHub repository with:
    - **Project ID**
    - **Region**
    - **GCR repository name**

   #### In this snippet

   ```
    substitutions:
    _PROJECT_ID: ''
    _REGION: 'us-central1'
    _ARTIFACT_LOCATION: 'us-central1-docker.pkg.dev'
    _REPO_NAME: ''
   ```
   
   Replace `PROJECT_ID`, `Region`, and `REPO_NAME` placeholders with actual values.

### 4. Set Up Cloud Function

**Enable apis and give the service account permissions if prompted to do so**

1. Create a **Cloud Function** that listens for changes to your GCS bucket:
   - Go to **Cloud Run Functions** → Create Function
   - Trigger Type: `Cloud Storage` 
   - Event Type: `google.cloud.storage.object.v1.finalized`
   - Bucket: Create any bucket in the same region or choose an already configured bucket
   - Leave everything else default and click next

2. Runtime: **Python 3.8**
   - Replace the **Entry Point** placeholder with `subscribe`.
   - Replace the `main.py` with the `cloudfunction.py` from the github repository.
   - Replace the values in the snippet based on your project configurations

    ``` 
    PROJECT_ID = 'your-project-id'                     # <---CHANGE THIS
    REGION = 'your-region'                             # <---CHANGE THIS
    ```


3. In the `requirements.txt`, ensure you have the following dependencies:

   ```
   google-api-python-client>=1.7.8,<2
   google-cloud-aiplatform[pipelines]
   ```

   ![Cloud Function Setup](https://drive.google.com/uc?export=view&id=1Kxn5XoXx1eKsZlHOR4z5v4FX2QONegKy) 

### 6. Commit and Push to GitHub

1. Now go to your **GitHub repository**, commit any changes, and push them to the `main` branch. This will:
   - Trigger the Cloud Build pipeline.
   - Upon completion, trigger the Cloud Function that will create and deploy your ML pipeline.

   ![GitHub Commit and Cloud Build Trigger](https://drive.google.com/uc?export=view&id=116o1G_kDCxu72w3AvZUqc0vO6PHNU5jB) 

   - You can also monitor the build in Cloud Build; This will take around 15 Minutes to execute. 

   ![Cloud Build Logs](https://drive.google.com/uc?export=view&id=1fmBx-hBuB0l5Apw012WL5cT6nU6e9c_d)

   - Once the cloud build gets completed you should see a `xgbpipeline` in `PROJECT_ID-bucket` bucket in Google Cloud storage.
   
   - This also automatically triggers the cloud function which detects the new yaml file and creates the ML pipeline.

   - You can then view the ML pipeline in Vertex AI Pipelines

   - ![Vertex AI Pipeline](https://drive.google.com/uc?export=view&id=1DSlhLdfyh_0bjqjINw8UaCiiTJAv_gY1)

**Note if you want to understand the individual components of the ML pipeline checkout `kfp\pipeline.py`**

## Conclusion

Once everything is set up correctly, every time you push changes to your `main` branch in GitHub, the pipeline will automatically build the Docker image, push it to GCR, and deploy the pipeline through Vertex AI, completing the CI/CD loop.


## Cleanup

Once you've finished testing or no longer need the resources, follow these steps to clean up your GCP environment to avoid unnecessary charges.

### 1. Delete Cloud Build Triggers

1. Go to **Cloud Build** → **Triggers** in the GCP console.
2. Select the triggers you created for the repository.
3. Click **Delete** to remove them.

### 2. Delete Cloud Functions

1. Go to **Cloud Run** → **Cloud Functions**.
2. Select the function you created for the pipeline trigger.
3. Click **Delete** to remove the function.

### 3. Delete Docker Images from GCR

1. Go to **Container Registry** in the GCP console.
2. Navigate to the repository you created.
3. Select the Docker images and click **Delete** to remove them from the registry.

### 4. Delete Service Accounts

1. Go to **IAM & Admin** → **Service Accounts**.
2. Find the service account you created for the pipeline.
3. Click on the service account and select **Delete**.

### 5. Disable Enabled APIs

1. Go to **APIs & Services** → **Enabled APIs & Services**.
2. Locate the following APIs you enabled during setup:
   - Vertex AI API
   - Cloud Build API
   - Cloud Run API
3. For each API, click **Manage** and then **Disable**.

### 6. Delete GCS Buckets

1. Go to **Cloud Storage** in the GCP console.
2. Find and select the bucket you used for the pipeline.
3. Click **Delete** to remove the bucket and its contents.

### 7. Delete the GCP Project (Optional)

If you created a dedicated project for this setup and no longer need it:
1. Go to the **IAM & Admin** → **Settings**.
2. Scroll down and click **Shut down** to delete the project entirely.

   **Note:** This will remove all resources associated with the project, including billing.
