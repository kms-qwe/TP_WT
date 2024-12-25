function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }   

    return cookieValue;
}


const likeSections = document.getElementsByClassName('question-like-section');

for (let section of likeSections) {
    const button = section.querySelector('#upButton');
    const counter = section.querySelector('#likeCount');

    button.addEventListener('click', () => {
        const formData = new FormData();
        formData.append('question_id', button.dataset.id);

        const request = new Request('/like/question/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        });

        fetch(request)
            .then((response) => response.json())
            .then((data) => {
                counter.textContent = data.count; 
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    });
}


const likeAnsSections = document.getElementsByClassName('answer-like-section');

for (let section of likeAnsSections) {
    const button = section.querySelector('#upButton');
    const counter = section.querySelector('#likeCount');

    button.addEventListener('click', () => {
        const formData = new FormData();
        formData.append('answer_id', button.dataset.id);

        const request = new Request('/like/answer/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        });

        fetch(request)
            .then((response) => response.json())
            .then((data) => {
                counter.textContent = data.count; 
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    });
}



const checkSections = document.getElementsByClassName('question-check-section');

for (let section of checkSections) {
    const checkButton = section.querySelector('#checkButton');
    const label = section.querySelector('label');
    const isCorrect = checkButton.checked;
    

    checkButton.addEventListener('change', function () {
        const answerId = checkButton.dataset.id;
        const formData = new FormData();
        formData.append('answer_id', answerId);
        formData.append('is_correct', checkButton.checked);

        const request = new Request('/answer/update/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
            }
        });

        fetch(request)
            .then((response) => response.json())
            .then((data) => {
                if (data.success) {
                    console.log('Answer correctness updated!');
                } else {
                    console.error('Error:', data.error);
                }
            })
            .catch((error) => {
                console.error('Error:', error);
            });
    });
}


