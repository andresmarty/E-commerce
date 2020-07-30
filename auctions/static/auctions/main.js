document.addEventListener('DOMContentLoaded', function() {

    const submit = document.querySelector('#submit');
    const newComment = document.querySelector('#newComment');

    submit.disabled = true;

    newComment.onkeyup = () => {
        if (newComment.value.length > 0) {
            submit.disabled = false;
        }
        else {
            submit.disabled = true;
        }
    }

});