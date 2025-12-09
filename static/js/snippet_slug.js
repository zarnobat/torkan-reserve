(function () {
    function persianSlugify(str) {
        return str
            .toLowerCase()
            .trim()
            .replace(/[\s\u200c]+/g, "-")
            .replace(/ي/g, "ی")
            .replace(/ك/g, "ک")
            .replace(/[^0-9a-zA-Zآ-ی\-]/g, "")
            .replace(/\-+/g, "-")
            .replace(/^\-+|\-+$/g, "");
    }

    document.addEventListener("DOMContentLoaded", () => {
        const nameInput = document.querySelector('input[name="name"]');
        const slugInput = document.querySelector('input[name="slug"]');

        if (nameInput && slugInput && !slugInput.value) {
            nameInput.addEventListener("input", () => {
                slugInput.value = persianSlugify(nameInput.value);
            });
        }
    });
})();
