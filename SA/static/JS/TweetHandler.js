//Start with first item (0)
let counter = 0;
// How many posts to load each time - In this case 10
const quantity = 10;

// When DOM loads, render posts.
document.addEventListener('DOMContentLoaded', load);

// If scrolled to bottom, load the next posts.
window.onscroll = () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        load();
        console.log("We out here!")
    }
};

// If hide button is clicked, then "hide" the post from the user.
document.addEventListener('click', event => {
    const element = event.target;
    if (element.className === 'hide') {
        element.parentElement.style.animationPlayState = 'running';
        element.parentElement.addEventListener('animationend', () =>  {
            element.parentElement.remove();
        });
    }
});



// Load next set of posts.
function load() {
    // Set start and end post numbers, and update counter.
    const offset = counter;
    const end = offset + quantity - 1;
    counter = end + 1;
    console.log(offset)
    console.log(end)

    //Get the user's archive of tweets we are viewing from the URL.
    var Pagestring = window.location.pathname
    var token = document.getElementById("token").innerHTML
    var res = Pagestring.split("/");
    var urlr = '/api/' +res[2] +'/tweets?offset=' + offset +'&end='+end +'&token='+ token
    console.log(urlr)

    // Open a new request to get posts.
    const request = new XMLHttpRequest();
    request.open('GET', urlr);
    request.onload = () => {
        console.log(request.response);
        var sample =request.response;
        var data =JSON.parse(request.response);

        console.log(typeof sample)
        console.log(typeof data)
        console.log(data)
        data.forEach(loadauthordata);


        //var data = JSON.parse(request.responseText);

        console.log("//////TWEET DATA")
        //console.log(data);
    };
    // Send request to url.
    request.send();
};




function loadauthordata(content) {
    // Set start and end post numbers, and update counter.


    //Get the user's archive of tweets we are viewing from the URL.

    var token = document.getElementById("token").innerHTML

    var urlr = '/api/'+content.author_id+'/data?type=author&token='+ token
    console.log(urlr)

    // Open a new request to get posts.
    const request = new XMLHttpRequest();
    request.open('GET', urlr);
    request.onload = () => {
        const data2 = JSON.parse(request.responseText);
        console.log("//////AUTHOR DATA")

          console.log(data2);
          console.log(content);
          add_post(content, data2);


    };
    // Send request to url.
    request.send();
};




// Add a new post with given contents to DOM.
const post_template = Handlebars.compile(document.querySelector('#post').innerHTML);

function add_post(tweet, author) {

    // Create new post.

    const post = post_template({'author_avatar': author.avatar, "author_handle": author.handle, "author_screename": author.screenname, "tweet_text": tweet.text, "tweet_likes": tweet.likes, "tweet_replies": tweet.replies, "tweet_retweets": tweet.retweets, "tweet_id": tweet.id, "tweet_sentiment": tweet.sentiment_score});

    // Add post to DOM.
    document.querySelector('#posts').innerHTML += post;
};
