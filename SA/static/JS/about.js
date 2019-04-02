var random_bg_images_array = [
  "https://source.unsplash.com/collection/852718/",
  "https://source.unsplash.com/collection/311958/",
  "https://source.unsplash.com/collection/289690/",
  "https://source.unsplash.com/collection/361687/",
  "https://source.unsplash.com/collection/996284/"
]


function RandomisedBGImage(){
  var bgpicker = random_bg_images_array[Math.floor(Math.random() * random_bg_images_array.length)];
  return bgpicker;
}

function ImageSwitcher(){
  var bgpicked = RandomisedBGImage()
  var imgpath = "url(" + bgpicked + ")"
  document.getElementById('bg').style.backgroundImage=imgpath;
}

setInterval(ImageSwitcher, 20000)
