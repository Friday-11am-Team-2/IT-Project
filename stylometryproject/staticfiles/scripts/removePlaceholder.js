let placeholder = document.querySelector("#curr-profile");
let docList = document.querySelector("#profile-list");

let profileAdded = false;

placeholder.addEventListener("click", () => {
    // remove placeholder text if there is a profile added
    if (docList.children.length > 1 && checkNoProfiles(docList.children)) {
        docList.children[0].remove();
        profileAdded = true;
    }

    // don't need this with current implementation because page refreshes when switched to it
    else {
        profileAdded = false;
    }
})

function checkNoProfiles(children) {
    for (let i = 0; i < children.length; i++) {
        if (children[i].id === "no-files") {
            return true;
        }
    }
    return false;
}