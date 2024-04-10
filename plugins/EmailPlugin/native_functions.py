from typing import Annotated

from semantic_kernel.functions import kernel_function


class EmailPlugin:
    @kernel_function(
        description="Send an email to one recipient.",
        name="SendAnEmail",
    )
    def send_an_email(
            self,
            recipient_name: Annotated[str, "The recipient name."],
            recipient_email: Annotated[str, "The recipient email."],
    ) -> Annotated[bool, "True: successfully sent the email. False: failed to send the email."]:
        return self.send_email_brevo(
            recipient_name=recipient_name,
            recipient_email=recipient_email
        )

    def send_email_brevo(
            self,
            recipient_name: str,
            recipient_email: str,
            subject: str = None,
            sender_name: str = None,
            sender_email: str = None,
            reply_to_name: str = None,
            reply_to_email: str = None,
            html_content: str = None,
    ):
        import sib_api_v3_sdk
        from sib_api_v3_sdk.rest import ApiException

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key[
            'api-key'] = 'YOUR_BREVO_API_KEY'

        api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
        subject = "You're Invited!! Collab Opportunities & TikTok Samples from SevenBox"
        sender = {"name": "Rena Ren", "email": "ren96098@gmail.com"}
        reply_to = {"name": "Rena Ren", "email": "ren96098@gmail.com"}
        # html_content = "<html><body><h1>This is a test email </h1></body></html>"
        html_content = self.get_html_content(name=recipient_name)
        to = [{"email": recipient_email, "name": recipient_name}]
        # params = {"parameter": "My param value", "subject": "New Subject"}
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, reply_to=reply_to,
                                                       html_content=html_content, sender=sender, subject=subject)

        try:
            api_response = api_instance.send_transac_email(send_smtp_email)
            print(api_response)
            return True
        except ApiException as e:
            print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)
            return False

    def get_html_content(self, name: str):
        return '''<html>
<body>
<p>Hi [name]</p>
<p>Thank you for showcasing SevenBox products!</p>
<p>I would like to invite you to our TikTok monetization space on Discord.💰 We will be sharing <b>flat-fee collab and free sample opportunities</b> for our exclusive TikTok creators.</p>
<p>Here, you will receive first-hand collab invitations from @sevenboxstore and other brands we partner with.</p>
<p>Click here to join our SevenBox Family: <a href="https://discord.gg/yyU2zRhv">SevenBox Discord</a></p>
<p>Best,</p>
<p>Rena | CEO of SevenBox</p>
<p><a href="https://www.tiktok.com/@sevenboxstore">@sevenboxstore</a></p>
</body>
</html>'''.replace("[name]", name)


# if __name__ == "__main__":
#     emailPlugin = EmailPlugin()
#     emailPlugin.send_email_brevo(recipient_name="abc", recipient_email="30000eric@gmail.com")
