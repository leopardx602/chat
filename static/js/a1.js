function send() {
  msg = document.getElementById("inputText").innerHTML
  if (msg) {
    //console.log(msg)
    data = `<div class="remote_box ">`
    data += `<div class="head_sticker ">`
    data += `<div class="pic ">`
    data += `<img src="https://picsum.photos/100/100?random=16 "/>`
    data += `</div>`
    data += `</div>`
    data += "<div class='remote_text'>" + msg + " </div>"
    data += `</div>`

    $("#content").append(data);
    $("#content").scrollTop($("#content")[0].scrollHeight);
  }
}

function send_r() {
  msg = document.getElementById("inputText").innerHTML
  if (msg) {
    //console.log(msg)

    today = new Date();
    data = `<div class="local_box">`
    data += "<div class='local_text'>" + msg + "</div>"
    data += `</div>`

    $("#content").append(data);
    $("#content").scrollTop($("#content")[0].scrollHeight);

    // post
    count = (msg.split("<img class=")).length - 1
    for (i = 0; i < count; i++) {
      start = msg.search("<img class=")
      end = msg.search('.gif">')
      tmp = msg.slice(start, end + 6);
      msg = msg.replace(tmp, "<<tiger01.gif>>");
    }
    //console.log(msg)
    nowTime = [today.getFullYear(), today.getMonth(), today.getDate(), today.getHours(), today.getMinutes()]
    js = JSON.stringify({
      'id': 'chen',
      'time': nowTime,
      'message': msg
    })

    $.post("/inputText", js, function(data, status) {
      //console.log(data, status)
    });
  }

  var today = new Date();
  today.getFullYear()
  today.getMonth()
  today.getDate()
  today.getHours()
  today.getMinutes()
  today.getSeconds()
  today.getMilliseconds()
}

function sticker() {
  data = document.getElementById("inputText").innerHTML
  count = (data.split("<img class=")).length - 1
  if (count < 3) {
    data = "<img class='gif' src='../static/img/tiger/A3.gif'>"
    $("#inputText").append(data);
  }
}

function sendOld(msg) {
  data = `<div class="local_box">`
  data += "<div class='local_text'>" + msg + "</div>"
  data += `</div>`
  return data
}

function oldMsg() {
  $.get("/oldMsg", function(data) {
    if (data) {
      preHeight = $("#content")[0].scrollHeight
      preTop = $("#content")[0].scrollTop

      data = data.reverse()
      Object.keys(data).forEach(key => {
        if (data[key]) {
          $("#content").prepend(sendOld(data[key]))
            //console.log(key, data[key]);
        }
      });

      nowHeight = $("#content")[0].scrollHeight
      $("#content").scrollTop(nowHeight - preHeight + preTop);
      console.log('height1:', preHeight)
      console.log('height2:', nowHeight)
    }
  });
}


$(document).ready(() => {
  $('#sticker').on('click', () => {
    if ($('#stickers').html().length != 0) {
      $('#stickers').html('')
      return
    }
    text = ''
    text += '<div id="sticker_head">'
    text += '<div>經典</div>'
    text += '<div onclick=sticker_change("tiger")>小虎</div>'
    text += '<div onclick=sticker_change("egg")>雞蛋</div>'
    text += '<div onclick=sticker_change("fox")>狐狸</div>'
    text += '<div id="sticker_close">關閉</div>'
    text += '</div>'
    text += '<div id="stickers_body">'

    for (i = 1; i <= 50; i++) {
      text += `<img class='gifIndex' id='tiger${i}' src='../static/img/tiger/tiger${i}.png'>`
        //console.log(`A${i}.gif`)
    }
    text += '</div>'
      //console.log(document.getElementById('sticker').offsetLeft)
      //console.log(document.getElementById('sticker').offsetTop)
    $('#stickers').html(text)

    $('.gifIndex').each(function() {
      $(this).hover(function() {
        path = $(this).attr('src').replace('.png', '.gif')
        $(this).attr('src', path);
      }, function() {
        path = $(this).attr('src').replace('.gif', '.png')
        $(this).attr('src', path);
      })

      $(this).on('click', () => {
        id = $(this).attr('id')
        data = document.getElementById("inputText").innerHTML
        count = (data.split("<img class=")).length - 1
        if (count < 3) {
          data = `<img class='gif' src='../static/img/tiger/${id}.gif'>`
          $("#inputText").append(data);
        }
      });
    })

    $('#sticker_close').on('click', () => {
      $('#stickers').html('')
    });
  });
})


function sticker_change(type) {
  console.log(type)
  text = ''
  for (i = 1; i <= 50; i++) {
    text += `<img class='gifIndex' id='${type}${i}' src='../static/img/${type}/${type}${i}.png'>`
      //console.log(`A${i}.gif`)
  }
  $('#stickers_body').html(text)

  $('.gifIndex').each(function() {
    $(this).hover(function() {
      path = $(this).attr('src').replace('.png', '.gif')
      $(this).attr('src', path);
    }, function() {
      path = $(this).attr('src').replace('.gif', '.png')
      $(this).attr('src', path);
    })

    $(this).on('click', () => {
      id = $(this).attr('id')
      data = document.getElementById("inputText").innerHTML
      count = (data.split("<img class=")).length - 1
      if (count < 3) {
        data = `<img class='gif' src='../static/img/${type}/${id}.gif'>`
        $("#inputText").append(data);
      }
    });
  })
}