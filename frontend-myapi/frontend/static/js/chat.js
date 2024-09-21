let emptyMessageCount = 0;
let blockSend = false;
let messageProcessing = false;

document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("messageInput");
    const sendButton = document.getElementById("sendButton");
    const client_id = getClientId(); // 로컬 스토리지에서 client_id 가져오기

    input.addEventListener('input', () => {
        adjustTextareaHeight(input);
    });

    input.addEventListener('keydown', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();  // 기본 Enter 키 동작(줄바꿈) 방지
            sendMessage(client_id);
        }
    });

    sendButton.addEventListener('click', function() { // 전송 버튼 클릭 이벤트 리스너 추가
        sendMessage(client_id);
    });

    loadMessagesFromLocalStorage();
});

function getClientId() {
    let client_id = localStorage.getItem('client_id');
    if (!client_id) {
        const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        const charactersLength = characters.length;
        client_id = '';
        for (let i = 0; i < 10; i++) {
            client_id += characters.charAt(Math.floor(Math.random() * charactersLength));
        }
        localStorage.setItem('client_id', client_id);
    }
    return client_id;
}

async function sendMessage(client_id) {
    if (blockSend || messageProcessing) return; // 메시지 생성 중이거나 전송이 차단된 경우 전송하지 않음

    const input = document.getElementById("messageInput");
    const messageText = input.value.trim();

    if (messageText === '') {
        emptyMessageCount++;
        if (emptyMessageCount >= 10) {
            blockSend = true;
            displayWarningMessage();
            setTimeout(() => {
                blockSend = false;
                removeWarningMessage();
            }, 5000);  // 5초 동안 전송 차단
        }
        return;
    }

    emptyMessageCount = 0;  // 메시지가 비어있지 않으면 카운트 초기화
    messageProcessing = true;

    // appendMessage("You", `client_id_${client_id}: ${messageText}`);
    appendMessage("You", messageText);
    input.value = "";

    // 응답 생성 중 메시지 추가
    const tempMessage = appendMessage("Bot", "답변을 생성중입니다", false, true);
    
    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ question: messageText, client_id: client_id })
        });
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }
        const data = await response.json();
        removeMessage(tempMessage); // 로딩 메시지 제거
        appendMessage("Bot", data.answer, true); // 실제 응답 메시지 추가
        // saveMessagesToLocalStorage();

    } catch (error) {
        console.error('error occurred while fetch:', error);
        updateMessage(tempMessage, '응답을 가져오는데 실패했습니다.'); // 로딩 메시지를 오류 메시지로 대체
    } finally {
        saveMessagesToLocalStorage();
        messageProcessing = false;
        input.style.height = 'auto';
        input.rows = 1;
    }
}

function removeMessage(messageWrapper) {
    clearInterval(messageWrapper.intervalId); // 기존 로딩 메시지 중지
    messageWrapper.remove(); // 메시지 제거
}

function appendMessage(sender, text, isHTML = false, isLoading = false) {
    const chatbox = document.getElementById("chatbox");
    const messageWrapper = document.createElement("div");
    messageWrapper.className = "message-wrapper";

    const messageElement = document.createElement("div");
    messageElement.className = "message";
    messageElement.classList.add(sender === "You" ? "sent" : "received");
    console.log(messageElement.classList);

    if (sender !== "You") {
        const avatar = document.createElement("img");
        avatar.src = "/static/images/bear.png"; // 업로드된 이미지 경로로 수정
        avatar.alt = "Chatbot Avatar";
        avatar.className = "avatar";
        messageElement.appendChild(avatar);
    }

    const paragraphElement = document.createElement("p");
    if (isLoading) {
        const intervalId = blinkingLoader(paragraphElement);
        messageWrapper.intervalId = intervalId; // intervalId를 messageWrapper에 저장
    } else {
        if (isHTML) {
            paragraphElement.innerHTML = marked.parse(text);
        } else {
            paragraphElement.textContent = text;
        }
    }
    messageElement.appendChild(paragraphElement);
    messageWrapper.appendChild(messageElement);
    chatbox.appendChild(messageWrapper);
    chatbox.scrollTop = chatbox.scrollHeight;

    return messageWrapper;
}

function updateMessage(messageWrapper, newText) {
    clearInterval(messageWrapper.intervalId); // 기존 로딩 메시지 중지
    const paragraphElement = messageWrapper.querySelector("p");
    paragraphElement.innerHTML = marked.parse(newText);
}


// 깜빡이는 로딩 메시지를 출력하는 함수
function blinkingLoader(element, delay = 100) {
    element.innerHTML = '답변을 생성중입니다';
    let dots = 0;
    const maxDots = 3;
    const intervalId = setInterval(() => {
      if (dots < maxDots) {
        element.innerHTML += '.';
        dots++;
      } else {
        element.innerHTML = '답변을 생성중입니다';
        dots = 0;
      }
    }, delay);
    return intervalId;
  }

function displayWarningMessage() {
    const chatbox = document.getElementById('chatbox');
    const warningMessage = document.createElement('div');
    warningMessage.id = 'warningMessage';
    warningMessage.classList.add('warning');

    const warningText = document.createElement('span');
    warningText.textContent = '5초 후에 다시 질문해주세요.';
    warningMessage.appendChild(warningText);

    chatbox.appendChild(warningMessage);
    warningMessage.scrollIntoView({ behavior: 'smooth' });
}

function removeWarningMessage() {
    const warningMessage = document.getElementById('warningMessage');
    if (warningMessage) {
        warningMessage.remove();
    }
}

function addInitialMessage() {
    const chatbox = document.getElementById('chatbox');
    const messageWrapper = document.createElement('div');
    messageWrapper.className = "message-wrapper";

    const messageElement = document.createElement('div');
    messageElement.className = "message received";

    const avatar = document.createElement("img");
    avatar.src = "/static/images/bear.png"; // 업로드된 이미지 경로로 수정
    avatar.alt = "Chatbot Avatar";
    avatar.className = "avatar";
    messageElement.appendChild(avatar);

    const paragraphElement = document.createElement('p');
    paragraphElement.innerHTML = '안녕하세요! 천재IT교육센터 챗봇<br>GenieNavi(지니나비) 입니다.<br>교육과정에 대해 질문해주세요.';

    messageElement.appendChild(paragraphElement);
    messageWrapper.appendChild(messageElement);
    chatbox.appendChild(messageWrapper);
}

function saveMessagesToLocalStorage() {
    const chatbox = document.getElementById('chatbox');
    const messages = Array.from(chatbox.getElementsByClassName('message-wrapper')).map(messageWrapper => {
        const messageElement = messageWrapper.querySelector('.message');
        const sender = messageElement.classList.contains('sent') ? 'You' : 'Bot';

        // // Function to get the full content from all nested <p> tags
        // const text = getFullMessageContent(messageElement);
        // console.log(text)
        const text = messageElement.querySelector('p').innerHTML

        return { sender, text };
    });
    localStorage.setItem('messages', JSON.stringify(messages));
}

// function getFullMessageContent(messageElement) {
//     const paragraphElements = messageElement.querySelectorAll('p');
//     let fullContent = '';

//     paragraphElements.forEach(paragraphElement => {
//         fullContent += paragraphElement.innerHTML + '\n';
//     });
    
//     return fullContent.trim();  // Remove the trailing newline character
// }


// textarea 높이 조절 함수
function adjustTextareaHeight(textarea) {
    const maxRows = 3; // 최대 줄 수
    const lineHeight = parseInt(window.getComputedStyle(textarea).lineHeight, 10); // 줄 높이
    textarea.style.height = 'auto'; // 높이를 초기화
    const newHeight = Math.min(textarea.scrollHeight, maxRows * lineHeight); // 새로운 높이 계산
    textarea.style.height = `${newHeight}px`; // 높이 설정
}

function loadMessagesFromLocalStorage() {
    const messages = JSON.parse(localStorage.getItem('messages'));
    if (messages && messages.length > 0) {
        messages.forEach(message => {
            appendMessage(message.sender, message.text, true);
        });
        const chatbox = document.getElementById("chatbox");
        chatbox.scrollTop = chatbox.scrollHeight; // 메시지를 로드한 후 스크롤을 맨 아래로 이동
    } else {
        addInitialMessage();
        const chatbox = document.getElementById("chatbox");
        chatbox.scrollTop = chatbox.scrollHeight; // 초기 메시지를 추가한 후 스크롤을 맨 아래로 이동
    }
}
