document.addEventListener("DOMContentLoaded", function() {
    // find all information icons
    const infoIcons = document.querySelectorAll(".info-icon");

    // for each info icon
    infoIcons.forEach(function(infoIcon) {

      // get the content of that icon
      const infoContent = infoIcon.querySelector(".info-content");
      
      // when the mouse hovers oven the icon
      infoIcon.addEventListener("mouseover", function() {

        // get the icon's popup bounding rectangle
        const iconRect = infoIcon.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const iconMiddleX = iconRect.left + iconRect.width / 2;

        // determine direction based on center of screen
        if (iconMiddleX < viewportWidth / 2) {
          infoContent.style.left = "100%";
        } else {
          infoContent.style.left = "auto";
          infoContent.style.right = "100%";
        }
        infoContent.style.display = "block";
      });
      
      // remove when mouse hover ends
      infoIcon.addEventListener("mouseout", function() {
        infoContent.style.display = "none";
      });
    });
  });