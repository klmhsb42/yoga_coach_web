

      


      /* TESTS */
      
      
      
      
      var socket = io.connect(window.location.protocol + '//' + document.domain + ':' + location.port);
      socket.on('connect', function(){
          console.log("Connected...!", socket.connected)
      });


      socket.on('message', function(data) {
           console.log(data);
      });




      /* UI */

      


      function openNav() {
        document.getElementById("mySidenav").style.width = "15%";
      }
      
      function closeNav() {
        if(document.getElementById("sidenav-pages").style.width != "0px"){
          document.getElementById("sidenav-pages").style.width = "0";
          setTimeout(function() {
            document.getElementById("mySidenav").style.width = "0";
          }, 300);
        }else{
          document.getElementById("mySidenav").style.width = "0";
        }
      }

      function openNavPages(page_id) {
        document.getElementById("sidenav-pages").style.width = "85%";
        
        $(".sidepage").hide();
        var page_id_str = "#sidepage-"+page_id;
        $(page_id_str).show();
      }


      $("#hide-popup").click(function(){
        $("#popup-container").hide();
      });
      
      $("#show-popup").click(function(){
        $("#popup-container").show();
      }); 

      

      $("#show-popup-inner").click(function(){
        $("#popup-container-inner").show();
        $("#popup-container-inner-cat").hide();
      }); 

      $("#hide-popup-inner").click(function(){
        
        $("#popup-container-inner-cat").show();
        $("#popup-container-inner").hide();
      }); 
      

      



      /* FEEDBACK */

      socket.on('score', function(data) {
        $("#score_val").text(data.score_val);
        $("#score_val").attr('style', 'color:'+data.score_color);
        $("#score_message").text(data.score_message);
        $("#score_message").attr('style', 'color:'+data.score_color);
      });

      socket.on('score_max', function(data) {
        $("#score_max").text(data.score_max);
        $("#score_max").attr('style', 'color:'+data.score_max_color);
        $("#score_max_message").text(data.score_max_message);
        $("#score_max_message").attr('style', 'color:'+data.score_max_color);
      });

      socket.on('instruction', function(data) {
           $("#instruction_txt").text(data.instruction_txt);
      });








      /* TIMER */
      
      socket.on('timer_socket', function(data) {
           $("#result").text(data.time);
      });

      

 



/* VIDEO */

/* setup video socket */

socket.on('response_back', function(image){
  photo.setAttribute('src', image );
});


/* global video variables */

var canvas = document.getElementById('canvas');
var context = canvas.getContext('2d');



  var videoDiv = document.getElementById("videoElement"),
  vendorUrl = window.URL || window.webkitURL;
  navigator.getMedia =    navigator.getUserMedia ||
                          navigator.webkitGetUserMedia ||
                          navigator.mozGetUserMedia ||
                          navigator.oGetUserMedia ||
                          navigator.msGetUserMedia;

  videoDiv.width = 700;
  videoDiv.height = 525;

var MediaStream;

/* setup webcam stream */

function captureWebcam(video, audio){
  navigator.getMedia({
      video: video,
      audio: audio
  }, function(stream){
      //videoDiv.src = vendorUrl.createObjectURL(stream);
      videoDiv.srcObject = stream;
      MediaStream = stream.getTracks()[0]; // create the stream tracker
  }, function(error){
      // An error occured
      // error.code
      console.log(error)
  }); 
}

/* setup video frame interval */

var refreshIntervalId = null;

function starttheinterval(interval_status){
  const FPS = 6;
  if(interval_status == true){
      if (refreshIntervalId !== null) return;
      refreshIntervalId = setInterval(() => {
        width=videoDiv.width;
        height=videoDiv.height;
        context.drawImage(videoDiv, 0, 0, width , height );
        var data = canvas.toDataURL('image/jpeg', 0.5);
        context.clearRect(0, 0, width,height );
        socket.emit('image', [data,1]);
    }, 1000/FPS);
  }else{
    clearInterval(refreshIntervalId);
    refreshIntervalId = null;
    
  }
}




/* AUDIO */



socket.on('audio_socket', function(data) {
  //console.log(data.audio_url);
  //new Audio(data.audiofile).play();
  //createaudioFile(data.audio_url);

  //url = data.audio_url
  //filename = data.audiofile
  //blobUrl = data.bloburl
  

  var getaudio = $("#audio-player").get(0);
  getaudio.src = "";
  getaudio.src = "static/audio/feedback.mp3";

  getaudio.load();
  getaudio.play();

});


async function createaudioFile(path) {
  // let response = await fetch(path);
  // let data = await response.blob();
  // let metadata = {
  //   type: 'audio/mp3'
  // };
  // let file = new File([data], "speech.mp3", metadata);
  // ... do something with the file or return it
  // console.log(file);
  // new Audio(file).play();
  
  // audio = file

  var importRes = await import(path);
  var audio = new Audio(importRes.default);
  audio.type = "audio/mpeg"; //"audio/mp3";
  try {
      await audio.play();
      console.log("Playing audio" + audio);
  } catch (err) {
      console.log("Failed to play, error: " + err);
  }
};



      

    
/*
function get_audio() {

	//var audiotext = "Please, raise your right arm 10% higher."

  var audiotext = [
    { "settxt":"Please, raise your right arm 50% higher." }
];



        $.ajax({
	   type: "POST",
	   url: "audio_feed",
	   data: JSON.stringify({'settxt': audiotext}),
     dataType: "json",
	   processData: false,
	   contentType: false,
	   success: (result) => {
	      //new Audio(result).play()
	      console.log(result);
	   },
	   error: (err) => {
	      console.log(err);
	   }
	});
*/

/*
  $.ajax({
        type: 'POST',
        url: '/audio_feed',
        data: JSON.stringify (audiotext),
        success: (result) => { 
          //alert('data: ' + data); 
          
	        console.log(result);
          //var mp3Url = 'static/speech.mp3';
          //$("#audio-player").attr('src', mp3Url);
          new Audio(result).play();
        },
        contentType: "application/json",
        dataType: 'json'
    });
    // stop link reloading the page
    event.preventDefault();

      }

*/
      

      /*
      const intervalID = setInterval(update_values, 1000);
      
      function update_values() {
        $.getJSON(
          root_url + "_timer?start='True'",
          data => {
            $("#result").text(data.result);
            if (data.result == 0) {
              clearInterval(intervalID);
            }
          }
        )
      }
*/




/* EXERCISES */

var slide_category = 0;

let slideIndex = 1;
showSlides(slideIndex);

function plusSlides(n) {
  showSlides(slideIndex += n);
}

function currentSlide(n) {
  showSlides(slideIndex = n);
}

function showSlides(n) {
  let i;
  let slides = document.getElementsByClassName("mySlides");
  
  if (n > slides.length) {slideIndex = 1}    
  if (n < 1) {slideIndex = slides.length}
  for (i = 0; i < slides.length; i++) {
    slides[i].style.display = "none";  
  }
  
  slides[slideIndex-1].style.display = "block";  
  
}



$(".hide-exercise-description").click(function(){
  $(".text").hide();
});

$(".show-exercise-description").click(function(){
  $(".text").show();
}); 



/* START AND STOP */

function startProcess(){
    captureWebcam(true, false);
    starttheinterval(true);
    var startdata = [slideIndex, slide_category, 1, 1]
    socket.emit('run', startdata);
    //get_audio();
    document.getElementById('button-start').disabled = true;
    document.getElementById('button-stop').disabled = false;
    document.getElementById('button-prev').disabled = true;
    document.getElementById('button-next').disabled = true;
}

function stopProcess(){
    MediaStream.stop();
    starttheinterval(false);
    $("#photo").attr('src', '');
    var startdata = [slideIndex, slide_category, 1, 0]
    socket.emit('run', startdata);
    document.getElementById('button-start').disabled = false;
    document.getElementById('button-stop').disabled = true;
    document.getElementById('button-prev').disabled = false;
    document.getElementById('button-next').disabled = false;
}
