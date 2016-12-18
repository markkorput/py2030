# Example project
This example project demonstrates how you can easily create a web-based interface to your network using py2030's WebServer component.

## Assumptions
The instructions below assume your computer has the py2030 package installed and that you have cd-ed into this example project folder.

## Usage
To start the app run the following command:
```shell
python -m py2030.app -p controller
```

Then open the following url in your web-browser:
http://localhost:2031

When you click the _start_ link on the web-page, note in your py2030 app's log that it sends out a /start OSC message.

When you click the _reload_ link on the web-page, note how the app reloads all its components. If you made any changes to the config.yml file, these will now go into effect.

When you click the _stop_ link on the web-page, note how the app shuts down.

## config.yml explanation
If you have a look at the [config.yml](config.yml), you see it configures a single profile with the name _controller_.

In the controller profile we configure two components; a web_server component and an osc_output component. The web_server component will serve the index.html file and process the ajax requests from the html file, the osc_output component responds to the internal _start_ event and broadcast a _/start_ OSC message over the local network.

Finally, the configuration file also specifies a reload_event and a stop_event, which notify the application to respectively reload and shutdown when the corresponding events are triggered (which the web_server is configured to do in response to the ajax-requests from the served html file).
