var random_bg_vid_array = [
  "code",
  "croc",
  "fan",
  "fish",
  "flam",
  "lulu",
  "meep",
  "modem",
  "riot",
  "money",
  "pigeon",
  "root",
  "swan",
  "vc",
  "hero"
]


function RandomisedVideo(){
  var vidpicker = random_bg_vid_array[Math.floor(Math.random() * random_bg_vid_array.length)];
  return vidpicker;
}

function VideoSwitcher(){
  var vidpicked = RandomisedVideo()
  var vidpath = "/static/images/video/" + vidpicked + ".mp4"
  var video = document.getElementById('video');
  var source = document.createElement('source');
  source.setAttribute('src', vidpath);
  video.appendChild(source);
  video.play();
}

VideoSwitcher()
