import base64
import json
from google.cloud import aiplatform

PROJECT_ID = 'your-project-id'                     # <---CHANGE THIS
REGION = 'your-region'                             # <---CHANGE THIS

def subscribe(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
        event (dict): Event payload.
        context (google.cloud.functions.Context): Metadata for the event.
    """
    # Extract the file that was uploaded
    file_name = event['name']
    bucket_name = event['bucket']
    
    # Optionally, you can check the file type to ensure it's a YAML or JSON
    if file_name.endswith('.yaml'):
        pipeline_spec_uri = f'gs://{bucket_name}/{file_name}'
        
        # Create payload JSON with just the pipeline_spec_uri
        payload_json = {
            "pipeline_spec_uri": pipeline_spec_uri
        }
        
        # Trigger the pipeline run with the file path as the spec
        trigger_pipeline_run(payload_json)

def trigger_pipeline_run(payload_json):

    pipeline_spec_uri = payload_json['pipeline_spec_uri']
    
    # Initialize the Vertex AI SDK
    aiplatform.init(
        project=PROJECT_ID,
        location=REGION,
    )
    
    # Create a PipelineJob with the specified pipeline YAML or JSON file
    job = aiplatform.PipelineJob(
        display_name='gcs-upload-triggered-pipeline',
        template_path=pipeline_spec_uri,
        enable_caching=False,

    )
    
    # Submit the job
    job.submit()
