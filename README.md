# Timezone Bot

An epic Discord bot that displays multiple time zones in its status, updating every minute.

<img width="247" height="93" alt="image" src="https://github.com/user-attachments/assets/1efd0b71-91fc-4046-879c-98ab7a87cc5d" />



## Using Render Free Tier To Keep App Running
* Render free plan can’t run Background Workers 24/7
* We run the bot as a Web Service with an HTTP health check endpoint
* A **GitHub Actions workflow** pings this endpoint every ~10 minutes so Render doesn’t put it to sleep  

```mermaid
flowchart TD
    A[Render Free Web Service] -->|Sleeps after 15 min idle| B[Stopped Bot]
    A --> C[healthz endpoint]
    D["GitHub Actions (pinger)"] -->|HTTP GET every ~10 min| C
    C -->|Activity| A
    A -->|Bot stays connected to Discord| E[Online Status + Timezones]
