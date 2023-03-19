function sendFormData() {
  const myField = document.getElementById('parking_location');
  const fieldValue = myField.value;
  const url = 'my-django-view';
  const data = {'my_data': fieldValue};
  const xhr = new XMLHttpRequest();
  xhr.open('POST', url, true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.setRequestHeader('X-CSRFToken', getCookie('csrftoken')); // Include CSRF token
  xhr.onreadystatechange = function() {
    if (xhr.readyState === 4 && xhr.status === 200) {
      const jsonResponse = JSON.parse(xhr.responseText);
      const nextOptions = jsonResponse.next_value;
      const nextSelect = document.getElementById('spaces');
      nextSelect.innerHTML = ''; // Remove existing options
      nextOptions.forEach(function(option) {
        const optionElement = document.createElement('option');
        optionElement.value = option.id;
        optionElement.text = option.name;
        nextSelect.appendChild(optionElement);
      });
    }
  };
  xhr.send(JSON.stringify(data));
}


  // Helper function to get CSRF token from cookie
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
  