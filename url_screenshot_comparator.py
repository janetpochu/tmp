import difflib
from PIL import Image
import numpy as np
import uuid
import os

original_folder = "report/original_images"
target_folder = "report/target_images"

# Function to compare two URLs and highlight only the difference in the target URL
def compare_urls(original_url, target_url):
    # Find common prefix
    prefix_len = 0
    min_len = min(len(original_url), len(target_url))
    while prefix_len < min_len and original_url[prefix_len] == target_url[prefix_len]:
        prefix_len += 1
    # Find common suffix
    suffix_len = 0
    while (
        suffix_len < (len(original_url) - prefix_len)
        and suffix_len < (len(target_url) - prefix_len)
        and original_url[-(suffix_len+1)] == target_url[-(suffix_len+1)]
    ):
        suffix_len += 1
    # Extract differing part
    target_diff = target_url[prefix_len:len(target_url)-suffix_len if suffix_len > 0 else len(target_url)]
    # Build highlighted target
    highlighted_target = (
        target_url[:prefix_len]
        + f'<span style="color:red;font-weight:bold">{target_diff}</span>'
        + (target_url[-suffix_len:] if suffix_len > 0 else "")
    )
    return (
        f'<div style="word-break:break-word;max-width:400px;">'
        f'<b>bef_redirect_url:</b> {original_url}<br>'
        f'<b>aft_redirect_url:</b> {highlighted_target}'
        f'</div>'
    )

# Function to compare two images pixel by pixel and highlight differences in red
def compare_images_pixel_by_pixel(original_path, target_path, diff_path):
    try:
        # Load images
        orig_img = Image.open(original_path).convert("RGB")
        targ_img = Image.open(target_path).convert("RGB")

        # Check if dimensions match
        if orig_img.size != targ_img.size:
            return False, "Images have different dimensions"

        # Convert to numpy arrays
        orig_array = np.array(orig_img)
        targ_array = np.array(targ_img)

        # Compare pixel by pixel
        diff_array = np.zeros_like(orig_array)
        identical = True
        for i in range(orig_array.shape[0]):
            for j in range(orig_array.shape[1]):
                if not np.array_equal(orig_array[i, j], targ_array[i, j]):
                    identical = False
                    diff_array[i, j] = [255, 0, 0]  # Mark difference in red
                else:
                    diff_array[i, j] = orig_array[i, j]  # Keep original pixel

        # Save difference image
        diff_img = Image.fromarray(diff_array)
        diff_img.save(diff_path)

        return identical
    except Exception as e:
        print(f"Error comparing images: {e}")
        return False, f"Error: {str(e)}"
# Function to generate HTML report
def generate_html_report(results, url_comparisons, image_comparisons_text,image_comparisons):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>URL and Screenshot Comparison Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; word-wrap: break-word; max-width: 300px; }
            th { background-color: #f2f2f2; }
            img { width: 200px; height: auto; transition: transform 0.3s; }
            img:hover { transform: scale(2); z-index: 100; position: relative; }
            .comparison-table td { vertical-align: top; }
            .result-section { margin-bottom: 40px; }
            .clickable:hover { cursor: pointer; background-color: #e0e0e0; }
        </style>
        <script>
            function scrollToResult(index) {
                document.getElementById('result-' + index).scrollIntoView({ behavior: 'smooth' });
            }
        </script>
    </head>
    <body>
        <h1>URL and Screenshot Comparison Report</h1>
        
        <!-- Part 1: Summary Table -->
        <h2>Summary of Comparisons</h2>
        <table>
            <tr>
                <th>Index with Original Link</th>
                <th>Compare 2 Actual URL Browser Results</th>
                <th>Compare Screen Result</th>
                <th>Click</th>
            </tr>
    """
    
    # Populate summary table
    for i, result in enumerate(results):
        original_link = result.split(',')[0]
        url_diff = url_comparisons[i]
        img_diff = image_comparisons_text[i]
        html_content += f"""
            <tr>
                <td>{i}_{original_link}</td>
                <td>{url_diff}</td>
                <td>{img_diff}</td>
                <td class="clickable" onclick="scrollToResult({i})">Click</td>
            </tr>
        """
    
    html_content += """
        </table>
        
        <!-- Part 2: Detailed Comparison Results -->
        <h2>Detailed Comparison Results</h2>
    """
    
    # Populate detailed comparison results
    for i, result in enumerate(results):
        fields = result.split(',')
        original_link = fields[0]
        original_screenshot = fields[2]
        target_screenshot = fields[5]
        diff_image = image_comparisons[i]
        original_screenshot = os.path.join( original_folder, original_screenshot + ".png")
        target_screenshot = os.path.join( target_folder, target_screenshot + ".png")
        html_content += f"""
            <div class="result-section" id="result-{i}">
                <h3>{i}_{original_screenshot}</h3>
                <table class="comparison-table">
                    <tr>
                        <th>Original</th>
                        <th>Target</th>
                        <th>Result of Comparison</th>
                    </tr>
                    <tr>
                        <td><img src="{original_screenshot}" alt="Original {i}"></td>
                        <td><img src="{target_screenshot}" alt="Target {i}"></td>
                        <td><img src="{diff_image}" ></td>
                    </tr>
                </table>
            </div>
        """
    
    html_content += """
    </body>
    </html>
    """
    
    with open("comparison_report.html", "w") as f:
        f.write(html_content)
    return "comparison_report.html"

# Main processing function
def process_results(results):
    url_comparisons = []
    image_comparisons = []
    image_comparisons_text =[]
    
    for i, result in enumerate(results):
        # Step 1: Split the result string
        fields = result.split(',')
        if len(fields) != 6:
            print(f"Skipping invalid record at index {i}: {result}")
            continue
        
        original_link = fields[0]
        original_redirect = fields[1]
        original_screenshot = fields[2]
        target_link = fields[3]
        target_redirect = fields[4]
        target_screenshot = fields[5]
        
        # Step 2: Compare URLs
        url_diff = compare_urls(original_redirect, target_redirect)
        
        #print(f"in main : url_diff ${url_diff}")
        url_comparisons.append(url_diff)
        
        # Step 3: Compare images
     
        
        orig_path = os.path.join( original_folder, original_screenshot + ".png")
        targ_path = os.path.join( target_folder, target_screenshot + ".png")
        diff_path = f"diff_{uuid.uuid4()}.png"
        
        image_comparisons_text.append(compare_images_pixel_by_pixel(orig_path, targ_path,diff_path))
        image_comparisons.append(diff_path)
    
    # Step 4: Generate HTML report
    report_path = generate_html_report(results, url_comparisons,image_comparisons_text, image_comparisons)
    return report_path

# Example usage
if __name__ == "__main__":
    # Sample data (replace with actual paths to images)
    sample_results = [
        "http://example.com,http://example.com/redirect&abc,fullpage_screenshot_,http://test.com,http://test.com/redirect?bcd,fullpage_screenshot_https___www_hangseng_com_en_hk_online_insurance",
        "http://example.org,http://example.org/redirect,screenshot_https___web_dev_articles_read_files_hl_zh_tw,http://test.org,http://test.org/redirect,screenshot_https___web_dev_articles_read_files_hl_zh_tw"
    ]
    
    report = process_results(sample_results)
    print(f"Report generated: {report}")