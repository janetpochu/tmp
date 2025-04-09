// background.js
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "captureVisibleTab") {
      console.info("Starting in background Capturing visible tab...");
      const { pixelRatio } = message;
      chrome.tabs.captureVisibleTab({ format: "png", quality: 100 }, (dataUrl) => {
        sendResponse(dataUrl);
        console.info("Process completed in background visible tab ");
        console.info("dataURL "+ dataUrl);
        //console.info("dataURL "+ dataUrl);
      });
      return true;
    }
  });
  