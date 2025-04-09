// Add this at the beginning of your file
const urlList = [
  'https://web.dev/articles/read-files?hl=zh-tw',
  'https://www.codedbrainy.com/capture-full-page-screenshots-chrome-extension/',
  // ... add your 10 URLs here
];

let currentUrlIndex = 0;

function processNextUrl() {
  console.info("Processing URL:", urlList[currentUrlIndex]);
  if (currentUrlIndex >= urlList.length) {
      console.log('All URLs processed');
      return;
  }

  const currentUrl = urlList[currentUrlIndex];
  
  // Navigate to the URL first
  chrome.tabs.update({ url: currentUrl }, (tab) => {
      // Wait for the page to load completely
      chrome.tabs.onUpdated.addListener(function listener(tabId, info) {
          if (tabId === tab.id && info.status === 'complete') {
              // Remove the listener
              chrome.tabs.onUpdated.removeListener(listener);
              
              // Wait a bit for any dynamic content to load
              console.info("Page started, waiting for 5 seconds...");
              setTimeout(() => {
                  takeScreenshot(tab, () => {
                      currentUrlIndex++;
                      processNextUrl();
                  });
              }, 5000); // Adjust timeout as needed
          }
      });
  });
}

function takeScreenshot(tab, callback) {
  chrome.tabs.sendMessage(tab.id, { action: "takeScreenshot" }, (response) => {
      const images = response.dataUrl;
    console.info("Received images:", images);
      if (images.length === 0) {
          console.error("No images captured for:", urlList[currentUrlIndex]);
          callback();
          return;
      }

      const canvas = document.createElement("canvas");
      const context = canvas.getContext("2d");
      const firstImage = new Image();

      firstImage.onload = () => {
          canvas.width = firstImage.width;
          canvas.height = images.length * firstImage.height;

          let imagesLoaded = 0;

          const drawImageOnCanvas = (image, index) => {
              context.drawImage(image, 0, index * firstImage.height);
              imagesLoaded++;

              if (imagesLoaded === images.length) {
                  const link = document.createElement("a");
                  link.href = canvas.toDataURL("image/png");
                  // Add URL to filename to distinguish screenshots
                  const filename = `screenshot_${urlList[currentUrlIndex].replace(/[^a-zA-Z0-9]/g, '_')}.png`;
                  link.download = filename;

                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                  
                  // Call the callback to process next URL
                  callback();
              }
          };

          images.forEach((dataUrl, index) => {
              const image = new Image();
              image.onload = () => drawImageOnCanvas(image, index);
              image.src = dataUrl;
          });
      };

      firstImage.src = images[0];
  });
}

// Modify your event listener to start the process
document.getElementById("takeScreenshotBtn").addEventListener("click", () => {
  processNextUrl();
  console.info("Started calling URLs");
});