document.getElementById("sendButton").addEventListener("click", sendMessage);
document
  .getElementById("userInput")
  .addEventListener("keypress", function (event) {
    if (event.key === "Enter") sendMessage();
  });

function sendMessage() {
  let userInput = document.getElementById("userInput").value.trim();
  if (userInput === "") return;

  let chatBox = document.getElementById("chatBox");
  chatBox.innerHTML += `<p><strong>You:</strong> ${userInput}</p>`;

  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query: userInput }),
  })
    .then((response) => response.json())
    .then((data) => {
      chatBox.innerHTML += `<p><strong>Bot:</strong> ${data.response}</p>`;
      chatBox.scrollTop = chatBox.scrollHeight; // Auto-scroll to the latest message
    })
    .catch((error) => {
      console.error("Error:", error);
      chatBox.innerHTML += `<p style="color: red;"><strong>Bot:</strong> Error fetching response.</p>`;
    });

  document.getElementById("userInput").value = ""; // Clear input field
}
