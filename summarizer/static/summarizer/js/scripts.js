// Add any JavaScript functionality here
console.log("Scripts loaded");

// Add smooth scrolling to all links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Form validation
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        let inputs = this.querySelectorAll('input[required]');
        inputs.forEach(input => {
            if (!input.value) {
                e.preventDefault();
                input.classList.add('error');
            } else {
                input.classList.remove('error');
            }
        });
    });
});

function displaySummary(summary, video) {
    const summaryContainer = document.getElementById('summary-container');
    summaryContainer.innerHTML = `
        <div class="card mb-3">
            <div class="row no-gutters">
                <div class="col-md-4">
                    ${video.thumbnail ? `<img src="${video.thumbnail}" class="card-img" alt="${video.title}">` : ''}
                </div>
                <div class="col-md-8">
                    <div class="card-body">
                        <h5 class="card-title">${video.title}</h5>
                        <h6>Short Description:</h6>
                        <p class="card-text">${summary.short_description}</p>
                        <h6>Key Points:</h6>
                        <ul>
                            ${summary.key_points.map(point => `<li>${point}</li>`).join('')}
                        </ul>
                        <h6>Full Summary:</h6>
                        <p class="card-text">${summary.full_summary}</p>
                        <a href="${video.url}" target="_blank" class="btn btn-primary">Watch Video</a>
                        <a href="${window.location.href}" class="btn btn-secondary">Summarize Another Video</a>
                    </div>
                </div>
            </div>
        </div>
    `;
}

document.addEventListener('DOMContentLoaded', function() {
    const summaryForm = document.getElementById('summary-form');
    if (summaryForm) {
        summaryForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            const actionUrl = this.getAttribute('action');

            console.log("Form submitted");
            console.log("Action URL:", actionUrl);

            fetch(actionUrl, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            }).then(response => response.json())
              .then(data => {
                  console.log("Response data:", data);
                  if (data.success) {
                      displaySummary(data.summary, data.video);
                  } else {
                      alert(data.error);
                  }
              });
        });
    }
});