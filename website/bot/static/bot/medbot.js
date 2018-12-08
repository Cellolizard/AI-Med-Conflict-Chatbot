$( document ).ready(function() {
    sessionStorage.clear();
});

// Scroll to the bottom of ele, and play scroll animation
function scroll(ele) {
    // var height = height < ele.scrollHeight ? ele.scrollHeight : 0;
    var height = ele.scrollHeight;
    this.stop().animate({
      scrollTop: height
    }, 1000});
  };
