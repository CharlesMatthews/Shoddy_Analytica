function ValidCheck() {
  //calls check for Twitter account existing
  var entry = document.getElementById("username").value;
  const Http = new XMLHttpRequest();
  //Build API Request URL

  if (entry != "") {
    var token = document.getElementById("token").innerHTML
    var urlr = '/api/verify?username=' + entry+'&token='+ token;
    console.log(urlr)
    Http.open("GET", urlr);
    Http.send();
    Http.onreadystatechange=(e)=>{
    var response = Http.responseText;
    //console.log(Http.responseText)
    const data = JSON.parse(Http.responseText);
    console.log("///////TEMP");
    console.log(data);
    console.log(data.valid);

    console.log("///////TEMP");

//    if (response.slice(0,1) == "t") {
    if (data.msg == "Available!" || data.msg == "Username is too short" || data.msg == "Username is too long") {
      console.log("No");
      var button = document.getElementById("subbut");
      button.disabled = true;

      var buttonII = document.getElementById("check");
      buttonII.className = "btn btn-outline-danger";
      buttonII.innerHTML = "Account does not exist"

      }else {
          console.log("Yes")
        //If ok then makes submit button clickable & then possible to request for scraping.
        var button = document.getElementById("subbut");
        button.disabled = false;
        var buttonII = document.getElementById("check");

        buttonII.className = "btn btn-outline-success";
        buttonII.innerHTML = "Account Verified"
      };
    };

  };
};



//document.getElementById("profimg").src =
  //https://twitter.com/kanyewest/profile_image?size=original
  //Makes request to own API to see if the account exists on Twitter
  //Unable to make a direct to twitter due to different domain. Gets caught in browsers as a dubious request.



  // readyState guide:
  //0   UNSENT  open() has not been called yet.
  //1   OPENED  send() has been called.
  //2   HEADERS_RECEIVED    send() has been called, and headers and status are available.
  //3   LOADING Downloading; responseText holds partial data.
  //4   DONE    The operation is complete.
  //200 status == OK
  // Therefore --- readyState 4 & status 200 --> request complete and ok response.

//Submit off to the API for scraping
