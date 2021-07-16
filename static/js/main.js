document.addEventListener('DOMContentLoaded', (event) => {

    // populate page with app launchers

    function populatePage() {
      var boxes = document.createDocumentFragment();

      for (var i=0; i < appdata.app_id.length; i++){
          var boxdiv = document.createElement('div');
          boxdiv.draggable = 'true';
          boxdiv.className = 'box';
          boxdiv.innerHTML = "<a href=\'"+appdata.link[i]+"\'>"+appdata.name[i]+" (" + appdata.description[i] + ")</a>";
          boxdiv.style = 'background-color:'+appdata.color[i];
          boxes.appendChild(boxdiv);
      }
      var cont = document.getElementById('boxcontainer');
      cont.appendChild(boxes);
    };

    populatePage();

  // drag and drop functionality below

  var dragSrcEl = null;

  function handleDragStart(e) {
    this.style.opacity = '0.4';
    dragSrcEl = this;

    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
    e.dataTransfer.setData('text/plain', this.style.backgroundColor);
  }

  function handleDragOver(e) {
    if (e.preventDefault) {
      e.preventDefault();
    }

    e.dataTransfer.dropEffect = 'move';

    return false;
  }

  function handleDragEnter(e) {
    this.classList.add('over');
  }

  function handleDragLeave(e) {
    this.classList.remove('over');
  }

  function handleDrop(e) {
    if (e.stopPropagation) {
      e.stopPropagation(); // stops the browser from redirecting.
    }

    if (dragSrcEl != this) {
      dragSrcEl.innerHTML = this.innerHTML;
      dragSrcEl.style.backgroundColor = this.style.backgroundColor;
      this.innerHTML = e.dataTransfer.getData('text/html');
      this.style.backgroundColor = e.dataTransfer.getData('text/plain');
    }

    return false;
  }

  function handleDragEnd(e) {
    this.style.opacity = '1';

    items.forEach(function (item) {
      item.classList.remove('over');
    });
  }


  let items = document.querySelectorAll('.container .box');
  items.forEach(function(item) {
    item.addEventListener('dragstart', handleDragStart, false);
    item.addEventListener('dragenter', handleDragEnter, false);
    item.addEventListener('dragover', handleDragOver, false);
    item.addEventListener('dragleave', handleDragLeave, false);
    item.addEventListener('drop', handleDrop, false);
    item.addEventListener('dragend', handleDragEnd, false);
  });
});