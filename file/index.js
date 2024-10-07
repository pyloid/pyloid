// CustomAPI method usage example

// Using the echo method
pylon.CustomAPI.echo('Hello', 42).then((result) => {
  console.log(result); // "Message received in Python: Hello, 42" output
});

// Using the getAppVersion method
pylon.CustomAPI.getAppVersion().then((version) => {
  console.log('App version:', version); // "App version: 1.0.0" output
});

// Example using async/await syntax
async function useCustomAPI() {
  try {
    const echoResult = await pylon.CustomAPI.echo('Test', 100);
    console.log(echoResult);

    const appVersion = await pylon.CustomAPI.getAppVersion();
    console.log('Current app version:', appVersion);
  } catch (error) {
    console.error('Error occurred during API call:', error);
  }
}

useCustomAPI();

// Button click event binding
document.getElementById('myButton').addEventListener('click', function () {
  // Using the create_window method
  pylon.CustomAPI.create_window().then((windowId) => {
    console.log('New window ID:', windowId); // "New window ID: [generated window ID]" output
  });
});

window.pylon.EventAPI.listen('pythonEvent', function (data) {
  console.log('Received event from Python:', data.message);
});
