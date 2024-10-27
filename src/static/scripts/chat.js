function scrollToBottom() {
    var messageBody = document.getElementById("messageFormeight");
    messageBody.scrollTop = messageBody.scrollHeight;
}

$(document).ready(function () {
    marked.setOptions({
        breaks: true,         // Line breaks in Markdown
        gfm: true,            // GitHub flavored markdown
        sanitize: false,      // Allow HTML (be cautious with this if handling user input)
    });
    
    $("#messageArea").on("submit", function (event) {
        event.preventDefault(); // Prevent form from submitting the default way

        const date = new Date();
        const hour = date.getHours();
        const minute = date.getMinutes();
        const str_time = hour + ":" + minute;

        var rawText = $("#text").val();
        if (!rawText.trim()) {
            return; // Don't send empty messages
        }

        // Append user's message
        var userHtml =
            '<div class="d-flex justify-content-end mb-4"><div class="msg_cotainer_send">' +
            rawText +
            '<span class="msg_time_send">' +
            str_time +
            '</span></div><div class="img_cont_msg"><img src="https://i.ibb.co/d5b84Xw/Untitled-design.png" class="rounded-circle user_img_msg"></div></div>';

        $("#text").val(""); // Clear the input
        $("#messageFormeight").append(userHtml);
        scrollToBottom();

        // Create a unique placeholder for the bot's response
        const botResponseId = 'botResponse_' + Date.now(); // Unique ID based on timestamp
        var botHtml =
            '<div class="d-flex justify-content-start mb-4"><div class="img_cont_msg"><img src="https://storage.googleapis.com/gb_chatbot_files_public/Jim%20profil.png" class="rounded-circle user_img_msg"></div><div class="msg_cotainer" id="' + botResponseId + '">' +
            '<span class="msg_time">' +
            str_time +
            '</span></div></div>';

        // Append the empty bot message container
        $("#messageFormeight").append($.parseHTML(botHtml));
        scrollToBottom();

        // Send the user's message to the server
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: new URLSearchParams({ prompt: rawText })
        })
        .then(response => {
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let result = '';

            // Function to read the streamed response
            function read() {
                reader.read().then(({ done, value }) => {
                    if (done) {
                        console.log("Stream finished");
                        return;
                    }

                    // Decode the streamed data
                    const chunk = decoder.decode(value, { stream: true });
                    console.log("Chunk received:", chunk); // Log each chunk for debugging
                    result += chunk;

                    // Parse result as Markdown using marked.js
                    const markdownContent = marked.marked(result);

                    // Update the bot response container with the Markdown content
                    $("#" + botResponseId).html(markdownContent + '<span class="msg_time">' + str_time + '</span>');

                    scrollToBottom();

                    // Continue reading the streamed response
                    read();
                });
            }

            // Start reading the streamed response
            read();
        })
        .catch(error => {
            console.error('Error receiving response:', error);
        });
    });
});
