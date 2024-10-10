// CustomAPI method usage example

// Using the echo method
pyloid.CustomAPI.echo('Hello', 42).then((result) => {
  console.log(result); // "Message received in Python: Hello, 42" output
});

// Using the getAppVersion method
pyloid.CustomAPI.getAppVersion().then((version) => {
  console.log('App version:', version); // "App version: 1.0.0" output
});

// Button click event binding
document.getElementById('myButton').addEventListener('click', function () {
  // Using the create_window method
  pyloid.CustomAPI.create_window().then((windowId) => {
    console.log('New window ID:', windowId); // "New window ID: [generated window ID]" output
  });
});

window.pyloid.EventAPI.listen('pythonEvent', function (data) {
  console.log('Received event from Python:', data.message);
});
