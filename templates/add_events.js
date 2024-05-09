$(document).ready(function () {
    $(".add").click(function () {
        let first = document.querySelector('form > p');
        let clone = first.cloneNode(true);
        first.parentNode.insertBefore(clone, first);
        return false;
    });

    // Event delegation for .remove elements
    $('form').on('click', '.remove', function () {
        $(this).parent().remove();
    });
});
