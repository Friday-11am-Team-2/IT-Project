document.addEventListener("DOMContentLoaded", function() {
    const infoIcons = document.querySelectorAll(".info-icon");
  
    infoIcons.forEach(function(infoIcon) {
      const infoContent = infoIcon.querySelector(".info-content");
  
      infoIcon.addEventListener("mouseover", function() {
        const iconRect = infoIcon.getBoundingClientRect();
        const viewportWidth = window.innerWidth;
        const iconMiddleX = iconRect.left + iconRect.width / 2;
  
        if (iconMiddleX < viewportWidth / 2) {
          infoContent.style.left = "100%";
        } else {
          infoContent.style.left = "auto";
          infoContent.style.right = "100%";
        }
  
        infoContent.style.display = "block";
      });
  
      infoIcon.addEventListener("mouseout", function() {
        infoContent.style.display = "none";
      });
    });
  });