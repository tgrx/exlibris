let pWebhookInfo = document.getElementById("id-webhook-info");
let buttonSetupWebhook = document.getElementById("id-setup-webhook");
let timer1 = undefined;

const API_V1 = "/api/v1";

document.addEventListener("DOMContentLoaded", setUp);


async function setUp() {
    buttonSetupWebhook.addEventListener("click", setupWebhookInfo);

    timer1 = setInterval(populateWebhookInfo, 4000);
    await populateWebhookInfo();
}


async function setupWebhookInfo() {
    const resp = await apiCall(`${API_V1}/setup_webhook`, {method: "PUT"});
    console.log(JSON.stringify(resp));
}


async function populateWebhookInfo() {
    const resp = await apiCall(`${API_V1}/get_webhook_info`, {method: "GET"});

    pWebhookInfo.innerText = JSON.stringify(resp);
}


async function apiCall(url, args = {}) {
    const headers = new Headers();

    headers.set("content-type", "application/json");

    const fetchArgs = {
        method: "GET",
        headers: headers,
        body: null,
    }

    if (args) {
        if (args.method) {
            fetchArgs.method = args.method;
            if (args.method !== "GET" && args.json) {
                fetchArgs.body = JSON.stringify(args.json);
            }
        }
    }

    const resp = await fetch(url, fetchArgs);

    if (resp.status !== 200) {
        return null;
    }

    return resp.json();
}
