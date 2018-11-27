var clientID="";

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
function getClientHistory(numResults){
chrome.history.search({text: '', maxResults: numResults}, function(data) {
    data.forEach(function(page) {
        alert(page.url);
    });
});
}


//Testing out storage 
function getClientID(callback){
	chrome.storage.sync.get('ID', callback);
}

function setClientID(value){
	chrome.storage.sync.set({'ID':value});
}

var input = prompt("Enter something to store");

setClientID(input);
getClientID(function (value){
	alert(value.ID);
});

