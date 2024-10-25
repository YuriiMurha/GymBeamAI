// Logout
document.getElementById('logoutBtn').addEventListener('click', () => {
    window.location.href = "index.html";
});

// Обробка опитування про здоров'я
document.getElementById('healthSurveyForm').addEventListener('submit', (e) => {
    e.preventDefault(); // Запобігаємо перезавантаженню сторінки

    // Отримуємо відповіді з форми опитування
    const gender = document.getElementById('gender').value;
    const exerciseFrequency = document.getElementById('exerciseFrequency').value;
    const dietType = document.getElementById('dietType').value;
    const waterIntake = document.getElementById('waterIntake').value;
    const chronicConditions = document.getElementById('chronicConditions').value;
    const sleepHours = document.getElementById('sleepHours').value;
    const healthRating = document.getElementById('healthRating').value;
    const stressFrequency = document.getElementById('stressFrequency').value;
    const smokeStatus = document.getElementById('smokeStatus').value;
    const alcoholConsumption = document.getElementById('alcoholConsumption').value;

    // Обробка результатів (можна відправити на сервер або зберегти)
    console.log("Survey completed:", {
        gender,
        exerciseFrequency,
        dietType,
        waterIntake,
        chronicConditions,
        sleepHours,
        healthRating,
        stressFrequency,
        smokeStatus,
        alcoholConsumption
    });

    // Ховаємо форму опитування
    document.getElementById('surveyContainer').style.display = 'none';

    // Відображаємо основний контент сторінки GymBeam Assistant
    document.getElementById('chatInputContainer').style.display = 'flex';
    document.getElementById('assistantContainer').style.display = 'block';
});

// Лічильник символів для текстового поля чату
const textarea = document.getElementById('chatInput');
const charCount = document.getElementById('charCountInside');

textarea.addEventListener('input', () => {
    charCount.textContent = `${textarea.value.length}/1000`;
});

// Обробка натискання на кнопку "Submit" для чату GymBeam Assistant
document.getElementById('submitBtn').addEventListener('click', () => {
    const userMessage = textarea.value.trim();
    const assistantChat = document.getElementById('assistantChat');

    if (userMessage.length > 0) {
        // Додавання повідомлення користувача в чат
        const userPrompt = document.createElement('div');
        userPrompt.classList.add('user-prompt');
        userPrompt.textContent = `User: ${userMessage}`;
        assistantChat.appendChild(userPrompt);

        // Відповідь GymBeam Assistant
        const assistantResponse = document.createElement('div');
        assistantResponse.classList.add('assistant-response');
        assistantResponse.textContent = "Assistant: Let me assist you with that. Processing your request...";
        assistantChat.appendChild(assistantResponse);

        // Очистити поле після відправки
        textarea.value = '';
        charCount.textContent = '0/1000';

        // Прокрутка до останнього повідомлення
        assistantChat.scrollTop = assistantChat.scrollHeight;
    }
});
