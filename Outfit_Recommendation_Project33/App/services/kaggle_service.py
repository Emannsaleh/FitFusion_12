import subprocess
import os
import time
import requests
import cloudinary
import shutil
import cloudinary.api
import cloudinary.uploader
from fastapi import BackgroundTasks
os.environ.pop("CLOUDINARY_URL", None)
DOWNLOAD_DIR = "outputs"

def clear_outputs():
    if os.path.exists(DOWNLOAD_DIR):
        shutil.rmtree(DOWNLOAD_DIR)

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    print("✅ outputs folder cleared")
def clear_old_results():
    try:
        resources = cloudinary.api.resources(
            type="upload",
            prefix="ITA_Results/",
            resource_type="image",
            max_results=100
        )

        for r in resources["resources"]:
            cloudinary.uploader.destroy(
                r["public_id"],
                resource_type="image"
            )

        print("✅ Old Cloudinary images removed")

    except Exception as e:
        print("❌ Failed to clear old results:", e)

cloudinary.config(
   cloud_name=,
    api_key=,
    api_secret=
)
def clear_old_status():
    try:
        cloudinary.uploader.destroy(
            "ITA_Results/job_status",
            resource_type="raw"
        )
        print("✅ Old status file removed")
    except Exception as e:
        print("❌ Status file delete failed:", e)

print("Cloudinary Cloud Name:", cloudinary.config().cloud_name)
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)
def download_image(url, filename):
    try:
        file_path = os.path.join(DOWNLOAD_DIR, filename)
        response = requests.get(url)
        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"✅ Image downloaded successfully at: {file_path}")
            return file_path
    except Exception as e:
        print(f"❌ Failed to download image: {e}")
    return None


def upload_output_image(image_path, folder_name="Final_Outputs", public_id="final_result"):
    try:
        result = cloudinary.uploader.upload(
            image_path,
            folder=folder_name,
            public_id=public_id,
            overwrite=True,
            resource_type="image"
        )
        print(f"✅ Output image uploaded to Cloudinary: {result['secure_url']}")
        return result['secure_url']
    except Exception as e:
        print(f"❌ Failed to upload output image: {e}")
        return None
def monitor_and_download_task(folder_name, status_file_id, check_interval=10, max_wait_minutes=30):
    print("🚀 Started monitoring Kaggle in background...")
    start_time = time.time()
    
    while True:
        elapsed = (time.time() - start_time) / 60  
        if elapsed > max_wait_minutes:
            print(f"⚠️ Timeout reached ({max_wait_minutes} minutes). Exiting monitor.")
            break

        try:
            try:
                resource = cloudinary.api.resource(
                    f"{folder_name}/{status_file_id}",
                    resource_type="raw"
                )
                file_url = resource["secure_url"]
                content = requests.get(file_url).text.strip()
            except cloudinary.exceptions.NotFound:
                print(f"⏳ Status file not found yet ({folder_name}/{status_file_id}), retrying in {check_interval}s...")
                time.sleep(check_interval)
                continue

            if content.lower() == "completed":
                print("✅ Kaggle finished! Searching for output image...")

                resources = cloudinary.api.resources(
                    type="upload",
                    prefix=f"{folder_name}/",
                    resource_type="image",
                    max_results=10
                )
                if not resources['resources']:
                    print("⚠️ No images yet, waiting...")
                else:
                    print("🖼 Images currently in folder:", [r['public_id'] for r in resources['resources']])
                    latest = resources['resources'][0]
                    image_url = latest['secure_url']
                    image_name = "result.jpg"
                    local_path = download_image(image_url, image_name)

                    if local_path:
                        upload_output_image(local_path)
                        break 

            else:
                print("⏳ File content isn't 'completed' yet, waiting...")

        except Exception as e:
            print(f"⏳ Waiting for status file... ({str(e)})")

        time.sleep(check_interval)

NOTEBOOK_PATH = "kaggle_notebook"

def run_kaggle_flow(input_dir, background_tasks: BackgroundTasks):

    clear_outputs()
    clear_old_results()
    clear_old_status()

    os.environ["PYTHONUTF8"] = "1"
    os.environ["KAGGLE_USERNAME"] = "emyysaleh"
    os.environ["KAGGLE_KEY"] = 

    result = subprocess.run(
        ["kaggle", "kernels", "push", "-p", NOTEBOOK_PATH , "--accelerator" , "NvidiaTeslaT4"],
        capture_output=True,
        text=True
    )
    print(result.stdout)
    print(result.stderr)

    if result.returncode == 0:
        print("Success ✅")
        monitor_and_download_task("ITA_Results", "job_status.txt")
    else:
        print("Error ❌")