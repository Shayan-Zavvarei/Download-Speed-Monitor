import requests
import time
import matplotlib.pyplot as plt
from tqdm import tqdm
import statistics
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_with_speed_monitor(url, output_file, verify_ssl=True):
    """
    Download file with speed monitoring and progress bar display
    """
    speeds = []
    timestamps = []
    
    print(f"Starting download from: {url}")
    
    try:
        # Get file information
        response = requests.get(url, stream=True, verify=verify_ssl, timeout=30)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        
        print(f"File size: {total_size / (1024*1024):.2f} MB")
        
        # Download settings
        chunk_size = 512 * 1024
        downloaded = 0
        start_time = time.time()
        last_time = start_time
        last_downloaded = 0
        
        # Progress bar
        progress_bar = tqdm(
            total=total_size,
            unit='B',
            unit_scale=True,
            desc='Downloading'
        )
        
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    chunk_len = len(chunk)
                    downloaded += chunk_len
                    progress_bar.update(chunk_len)
                    
                    current_time = time.time()
                    time_diff = current_time - last_time
                    
                    if time_diff > 0:
                        bytes_diff = downloaded - last_downloaded
                        speed_mbps = (bytes_diff / time_diff) / (1024 * 1024)
                        
                        speeds.append(speed_mbps)
                        timestamps.append(current_time - start_time)
                        
                        last_time = current_time
                        last_downloaded = downloaded
        
        progress_bar.close()
        
        # Calculate statistics
        total_time = time.time() - start_time
        avg_speed = (downloaded / total_time) / (1024 * 1024)
        
        print(f"\n✓ Download completed!")
        print(f"Total time: {total_time:.2f} seconds")
        print(f"Average speed: {avg_speed:.2f} MB/s")
        
        if speeds:
            print(f"Maximum speed: {max(speeds):.2f} MB/s")
            print(f"Minimum speed: {min(speeds):.2f} MB/s")
            print(f"Standard deviation: {statistics.stdev(speeds):.2f} MB/s")
        
        return speeds, timestamps, avg_speed
    
    except requests.exceptions.SSLError as e:
        print(f"\n✗ SSL Error: {e}")
        print("Try using verify_ssl=False or use HTTP URL instead")
        return [], [], 0
    except requests.exceptions.RequestException as e:
        print(f"\n✗ Download Error: {e}")
        return [], [], 0

def plot_results(speeds, timestamps, avg_speed):
    """
    Plot analytical graphs of download speed
    """
    fig, axes = plt.subplots(2, 1, figsize=(12, 10))
    
    # First graph: Speed over time
    axes[0].plot(timestamps, speeds, 
                 linewidth=1.5, 
                 color='#2E86AB', 
                 label='Instantaneous Speed',
                 alpha=0.7)
    axes[0].axhline(y=avg_speed, 
                    color='#E63946', 
                    linestyle='--', 
                    linewidth=2,
                    label=f'Average: {avg_speed:.2f} MB/s')
    axes[0].fill_between(timestamps, speeds, alpha=0.3, color='#2E86AB')
    axes[0].set_xlabel('Time (seconds)', fontsize=12)
    axes[0].set_ylabel('Speed (MB/s)', fontsize=12)
    axes[0].set_title('Download Speed Over Time for Your Internet Provider', fontsize=14, fontweight='bold')
    axes[0].legend(loc='upper right')
    axes[0].grid(True, alpha=0.3, linestyle='--')
    
    # Second graph: Speed distribution histogram
    axes[1].hist(speeds, bins=30, color='#06A77D', alpha=0.7, edgecolor='black')
    axes[1].axvline(x=avg_speed, 
                    color='#E63946', 
                    linestyle='--', 
                    linewidth=2,
                    label=f'Average: {avg_speed:.2f} MB/s')
    axes[1].set_xlabel('Speed (MB/s)', fontsize=12)
    axes[1].set_ylabel('Frequency', fontsize=12)
    axes[1].set_title('Download Speed Distribution-Your Internet Provider', fontsize=14, fontweight='bold')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3, axis='y', linestyle='--')
    
    plt.tight_layout()
    plt.savefig('download_speed_analysis-Your Internet Provider.png', dpi=300, bbox_inches='tight')
    print("\n✓ Chart saved: download_speed_analysis-Your Internet Provider.png")
    plt.show()

if __name__ == "__main__":
    # فایل تست 50MB از Cloudflare
    test_url = "https://speed.cloudflare.com/__down?bytes=104857600"
    output_filename = "Your Internet Provider_test_file_100mb.bin"
    
    speeds, timestamps, avg_speed = download_with_speed_monitor(test_url, output_filename)
    
    if speeds and timestamps:
        plot_results(speeds, timestamps, avg_speed)
    else:
        print("\n⚠️ Download failed. Try another URL.")
