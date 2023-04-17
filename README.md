# GenericRESTAPI
> A simple framework for implementing a small REST API server

## Directory
- [Installation](#installation)
- [Request Requirements](#request-requirements)
	- [Request Path Requirements](#request-path-requirements)
	- [Form Data](#form-data)
	- [URL Arguments](#url-arguments)
- [Response Info](#response-info)
	- [Common Values](#common-values)
- [Authentication](#authentication)
	- [Basic](#basic)
	- [Bearer](#bearer)
- [Creating Your Own Apps](#creating-your-own-apps)
	- [App Structures](#app-structures)
	- [Action Args](#action-args)
	- [Action Returns](#action-returns)
	- [Base Actions](#base-actions)
	- [App Isolation](#app-isolation)
	- [Installing To Docker](#installing-to-docker)
- [Configurable Items](#configurable-items)
	- [Globe](#globe)
	- [Disabling Apps, Methods, and Actions](#disabling-apps-methods-and-actions)
	- [Redirecting Actions](#redirecting-actions)
	- [Docker Modifications](#docker-modifications)
- [To-Do](#to-do)
- [Bugs](#bugs)

---

## Installation
## Straight
This server runs straight from the directory; There is no installation

## Docker
You can build a Docker image using the provided ```Dockerfile```. Below are some instructions on building:

1. From within the repo directory: ```docker build -t grest_image .```
2. ```docker run -dp 8080:8080 --name grest_server grest_image```
> Note: The default port is 8080. This can be changed via the "SERV_PORT" var. See [Configurable Items](#configurable-items).
3. An instance should be running now! To run from a container: ```docker start grest_server```

---

## Request Requirements
### Request Path Requirements
Because this is a REST API server, it's meant to take requests as such. The uses of request methods such as "GET", "POST", etc... Should all be used as expected (this really just comes down to how you write your apps). The most important thing to note is that the request path is **case sensitive** and follows the following syntax: ```/api/app/action```

> - "api" is constant and required
> - "app" is the name of the requested app
> - "action" is the name of the requested action to be performed

### Form Data
All requests that contain form data **must** contain a "Content-Length" header.

If a "Content-Type" header is passed and the server supports that type, it will automatically parse the data and give the results to the action.
There are currently 2 content types supported by this server:
-	application/x-www-form-urlencoded
  - **Returns a dict**
	- Does not attempt to decode values from url encoding (you can do this manually using ```parsing.decodeURLEncoding()``` function)
-	application/json
	- **Returns a dict**
	- Leverages the builtin ```json.loads()``` function

If the content type isn't specified, is unrecognized by the server, or threw an error while parsing, it will just pass the raw data to the action

### URL Arguments
URL arguments can be passed just like any other HTTP request. For example, if we wanted to pass the value "True" as the arg "time_only" to the app "Time/now", we can do so like this:
```
curl -k 'https://localhost:8080/api/Time/now?time_only=True'
```

To pass multiple arguments, separate them with ```&```. Ex: if we also want to get a specific format back, we can pass a base64 encoded formatting string ("Year: %Y\nMonth: %m\nDay: %d" -> "WWVhcjogJVlcbk1vbnRoOiAlbVxuRGF5OiAlZA==") to the "format" arg:
```
curl -k 'https://localhost:8080/api/Time/now?time_only=True&format=WWVhcjogJVkKTW9udGg6ICVtCkRheTogJWQ='
```

---

## Response Info
### Common Values
Responses are expected to be returned as JSON. Most functions and classes revolve around this and will default to JSON whenever possible. All JSON responses are strongly suggested to have at least all of the following:
- status: A string with value "OK" or "Failed"
- response: The response data. This can be the data returned for a request, or an error message.

A common value (but not required!) returned with errors is "extra", which will contain extra information about the error. Normally this will be common reasons for failures

When creating your own apps, it is strongly recommended to use the reply.Reply() class and it's subclasses (See [Action Returns](#action-returns))

---

## Authentication
Currently, the server supports the following authentication methods:
- Basic
- Bearer

To authenticate the user, you must create a ```parsing.Auth``` object and call the appropriate authentication method from it.

The ```parsing.Auth``` object will always return a valid (conforms to our standards) dict object. The advantage to this is if there are any errors while authenticating, all you need to do is check the value of "status"

Optionally, you can specify an sqlite3 database and any columns to return when creating the auth object. To do this, some requirements must be met. Different auth schemas require different layouts:

```
Table: [tokens]
Cols: (token BLOB)
Required by:
	- bearer

Table: [auth]
Cols: (username VARCHAR, password VARCHAR)
Required by:
	- basic
```

> Note: If returning specific columns, pass a list of column names as they would appear in the table

### Basic
The basic form of authentication is to pass a header with a base64 encoded ```username:password``` string:
```
Authorization: Basic abcdefg
```

Here is the cURL command to test basic authentication with the given "DummyAuth" app. This assumes the server is running locally on port 8080, using the default certs:
```
curl -k https://localhost:8080/api/DummyAuth/basic -H "Authorization: Basic YmFzaWNfdGVzdGVyOmJhczFjOnBhc3N3MHJkIQ=="
```

### Bearer
If your app should use a token instead, you can use the "Bearer" schema. Same as "Basic", but you pass a base64-encoded token, which will be compared against a bytes object instead of a string. This means a token can be created using bytes instead of characters.

Below is the cURL command to test bearer auth with the "DummyAuth" app:
```
curl -k https://localhost:8080/api/DummyAuth/bearer -H "Authorization: Bearer 2RRdjEqDbiSzq+4o/MwciEoqjpXYVeZIrkiA5g93qHY="
```

---

## Creating Your Own Apps
### App Structures
To create your own app, the following must exist:
- A directory under "Apps", named the same as the app.
- A directory under the app for each supported request method (GET, POST, etc...). Make sure these are all caps
- A/multiple python scripts under each method directory. These are the actions callable by clients.

> Note: The name of the directory in "Apps" is the exact **case sensitive** name used in a request

Here is a directory tree of an app named "TestApp", that supports GET and POST methods. This is what should be seen from the OS:

```
Apps
  |_ TestApp
       |_ GET
       |   |_ list_alerts.py
       |
       |_ POST
            |_ create_alert.py
```

All action scripts **must** have a function named "action". This is what will be run when called by a client.

### Action Args
All actions are given 3 keyword args in this order:
1. **request_headers** _(dict)_: A dictionary of request headers. This is useful if a client is passing data such as authentication, or (for example) your app relies on user agent data
2. **request_data** _(bytes)_: Raw form data
3. **url_args** _(dict)_: A dictionary of given url arguments (https://localhost:8080/api/Time/now?format=abc)

### Action Returns
All actions must return Reply objects. These are provided via the ```reply``` module. Most builtin Reply objects and it's subclasses are built to return JSON data whenever possible. We will assume you are returning JSON objects from hereon out.

The standard I'm looking to follow is for all actions to return at least the following:
- status: Either "OK" or "Failed"
- response: Error info, or action results

Many errors (not all!) can return with a key "extra". This will hold additional hints as to why the error occurred.

There are some functions to return pre-built Reply objects that follow this standard. They are found in the "reply.py" file and can be invoked by importing "reply" into your actions:
	- reply.Ok.JSONResponse: Given a "response" string, returns {"status":"OK","response":response}
	- reply.Failed.JSONResponse: Given a "response" string, returns {"status":"Failed","response":response}
> Note: Both the above functions can include more items by passing them to the functions as args.
> Ex: If I wanted to include and "extra" in the genericFailed I would call it like: genericFailed("Invalid input",extra="The client gave bad data")

### Base Actions
**NOTE**: This has NOT been implemented yet!
If desired, it is possible to specify a catch-all action.

Take the following url as example (assuming a GET request): "https://localhost:8080/api/Info/". Because there is no action specified, the server will return an error. We can remediate this by creating an action named "base". Any requests that either don't have an action or that pass a non-existing action will be redirected to this.

This allows the server to follow the RESTful ideology closer, and allows a simpler way to interact with the server. Take this DELETE request as example: "https://localhost:8080/api/DummyAuth/tester". With a base action, we can extract the final target from the URL (in this case a username "tester") and have the base action delete that user from the authentication database. To enable this functionality, in the ```base.py``` file you need to:
- Set the variable ```action_as_input``` to ```True``` (see ```Apps/Time/POST/base.py``` for examples)
- Include the argument ```base_input``` in the action function def. This is how the requested action is passed as input to the base action. It is passed as a string.

### App Isolation
Apps are not isolated from one another. It is not explicitly simple to interact with other apps, but it can be done. One thing to keep in mind is that the working directory is NOT wherever the app resides, but is at the top level of this project.

For example, the Info/apps app returns a list of all loaded apps and their actions. This is done by iterating through globe.ALL_APPS. We can simply import globe as we would normally (i.e. we don't need something like ```import ..globe```)

### Installing To Docker
If you've created a docker container and want to add new Apps, you don't need to rebuild the image. You can simply copy the new Apps right into the container (assuming they are under a local dir named ```Apps```:
```docker cp ./Apps/. <container name>:/opt/Grest/Apps```
> Note: The trailing ```/.``` after the source is CRITICAL! This tells Docker that we want to copy all contents

---

## Configurable Items
### Globe
The ```globe.py``` file holds all configurable items. Think of it as a config file, but in Python! Any comment blocks that use triple quotes (some editors might make these blocks a different colour) are editable by you. Here are the explanations of all items in this file:
- main.py
	- **SERV_IP** _(str)_: The IP the server will bind to
	- **SERV_PORT** _(int)_: The port the server will run on
	- **SERV_TIMEOUT** _(int)_: The seconds the server will stay connected to the client
	- **CLI_TIMEOUT** _(int)_: The seconds the server will wait for the client
	- **CLI_BLOCKING** _(bool)_: Boolean to determine if the client sockets are blocking or not (True is blocking)
	- **THREAD_COUNT** _(int)_: The number of listener threads to run at once. This equates to the number of simultaneous connections.
- clients.py
	- **SUPPORTED_METHODS** _(list of strs)_: A list of all supported request methods. Essentially a list of allowable method directory names (see [App Structures](#app-structures))
- TLS
	- **CERT_PATH** _(str or None)_: Path to the TLS Certificate. If both CERT_PATH and KEY_PATH aren't set, server won't encrypt
	- **KEY_PATH** _(str or None)_: Path to TLS private key. If both CERT_PATH and KEY_PATH aren't set, server won't encrypt

### Disabling Apps, Methods, and Actions
To disable apps, methods, and/or actions, create a file under the "Apps" directory named "disabled". Each line can only have one disable entry and must follow the following syntax. To disable:
- Apps: ```app```
- Methods: ```app.method```
- Actions: ```app.method.action```

>Ex: To disable all GET methods from the Time app, we would add a line ```Time.GET``` to the "disabled" file

You can use ```#``` to comment out lines in that file.

### Redirecting Actions
If you'd like to change the name of an action without changing the Python file's name, you can implement redirects. By adding a file named ```redirect``` in the same directory as an action, you can set a different name for the action.
There must be only one redirection per line in the ```redirect``` file.
The syntax follows:

```
## Empty lines or lines starting with a '#' are ignored
## Note that the spaces before and after the arrow are required!

orig_action -> new_action
```

There are 5 options to redirection naming:
	- Static: Just using a name that will not change
		- Takes a valid URL compliant string
	- **[NOT IMPLEMENTED]** Dynamic: Change the name each time it is requested
		- Takes ```?``` followed by either "random" or "hex random" characters
		- Remaining specifications follow "random" or "hex random" as detailed below
	- Random: The server generates a random action name
		- Takes ```*``` as the new name
		- Uses charset: ```a-zA-Z0-9_```
		- Adding a number directly after the ```*``` will specify the length
		- Adding two numbers separated by a dash will specify a random range (inclusive)
		- Default length is 16-32 chars long, randomly chosen by server
	- Hex Random: The server generates a random action name (same as "Random"), but uses only lowercase hex chars
		- Takes ```&``` as the new name
		- Uses charset: ```a-f0-9```
		- Adding a number directly after the ```*``` will specify the length
		- Adding two numbers separated by a dash will specify a random range (inclusive)
		- Default length is 16-32 chars long, randomly chosen by server
	- Aliasing: Point a static non-existent name to an existing action
		- Takes a valid URL compliant string
		- Does not change the name of the original action, just points a new name to it

Check out the example in the "Info" app: ```Apps/Info/GET/redirect```

### Docker Modifications
When running the server as-is, you can simply edit the ```globe.py``` file. You can do the same for the docker container if you change the configs before building the image. If you've already built the image but need to change things, you can run the following to edit the config file: ```docker exec -u 0 -it grest_demo /bin/nano globe.py```

---

## To-Do
- Allow for an interrupt signal to tell the server to refresh apps (instead of having to restart the entire server)
- Implement dynamic action naming
- Enable ```multipart/form-data``` parsing
	(Update 1): Created new method of parsing Content-Type headers. Just need to write the parsing function and it should be done!
	(Update 2): It is splitting by boundaries, but only one file can be properly processed at a time it seems (at least when multiple files are send via cURL)
- [Completed 2022.08.30] ~~Update ```conn.genericFailed()``` so the server doesn't return a 200 OK with it. Because it's a generic error the return status will probably just be a 500 Internal Server Error, but will still be customizable by the user~~ Now uses the Reply class solution
- [Completed 2022.07.25] ~~Accept GET url args~~
- [Completed 2022.08.21] ~~Implement a "base" action, where any request that doesn't match an existing action will redirect to the "base" action. See [Base Actions](#base-actions).
	(Update 1): Having issues with getting the Method class to detect the base action~~

## Bugs
- [False Positive 2022.08.17] ~~Sending a request with Content-Length header of 0 will crash the assigned thread~~ Requests with Content-Length of 0 will **not** be parsed because a 0 will be interpreted as boolean ```False```
