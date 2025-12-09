function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = cookie.substring(name.length + 1);
                break;
            }
        }
    }
    return cookieValue;
}

const likeBtn = document.getElementById("like-btn");
const likeIcon = document.getElementById("like-icon");

if (likeBtn) {
    const initialLiked = likeBtn.dataset.liked === "true";
    likeIcon.style.fill = initialLiked ? "red" : "gray";
}

likeBtn.addEventListener("click", function (e) {
    e.preventDefault();

    const url = this.dataset.url;
    const csrftoken = getCookie("csrftoken");

    fetch(url, {
        method: "POST",
        headers: {
            "X-CSRFToken": csrftoken,
        },
    })
        .then((r) => r.json())
        .then((data) => {
            likeIcon.style.fill = data.liked ? "red" : "gray";
            document.getElementById("likes-count").innerText = data.likes_count;

            likeBtn.dataset.liked = data.liked ? "true" : "false";
        })
        .catch((err) => console.error("JSON error:", err));
});
