//document.addEventListener('DOMContentLoaded', loaddash);



//function getdata(url, id) {
//  var xhr = new XMLHttpRequest();

//  xhr.onreadystatechange = function() {
//    if (xhr.readyState === 4) {
//      console.log(xhr.response);
//      add_post(id, xhr.response);
//
//    }
//  }
//  xhr.open('GET', url, true);
//  xhr.send('');

//}

//function loaddash() {
//  var token = document.getElementById("token").innerHTML///
//
//  var apitoptweets='/api/*/toptweet?end=3&token=' + token;
//  getdata(apitoptweets, "#toptweet");
//  console.log(apitoptweets);
//  var apirecenttweets='/api/*/tweets?end=3&token=' + token;
//  getdata(apirecenttweets,"#recent");
//  console.log(apirecenttweets);
//  var apirandom='/api/*/tweets?end=1&random=true&token=' + token;
//   getdata(apirandom, "#random");
//    console.log(apirandom);
//}




//function add_post(id, contents) {

//  var post_template = Handlebars.compile(document.querySelector(id).innerHTML);

//    // Create new post.
//    const post = post_template({'contents': contents});

//    // Add post to DOM.
//    document.querySelector(id).innerHTML += post;
//};
