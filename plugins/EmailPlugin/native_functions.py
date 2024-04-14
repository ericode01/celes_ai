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
        subject = "COLLAB INVITE💌We pay for your samples on TikTok!"
        sender = {"name": "SevenBox", "email": "rena.sevenbox@gmail.com"}
        reply_to = {"name": "SevenBox", "email": "rena.sevenbox@gmail.com"}
        # html_content = "<html><body><h1>This is a test email </h1></body></html>"
        html_content = self.get_html_content_2(name=recipient_name)
        to = [{"email": recipient_email, "name": recipient_name}]
        # params = {"parameter": "My param value", "subject": "New Subject"}
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, reply_to=reply_to,
                                                       html_content=html_content, sender=sender, subject=subject)

        try:
            #if recipient_name == "testuser1" or recipient_name == "renasevenbox" or recipient_name == "testuser2":
            api_response = api_instance.send_transac_email(send_smtp_email)
            print(api_response)
            print(f"Sending email. Name:{recipient_name}. Email:{recipient_email}")
            # print(api_response)
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


    def get_html_content_2(self, name: str):
        return '''<html>
<body>
<p>Dear [@handle],</p>
<p>You’ve been selected for a personalized collaboration invite from @sevenboxstore. Enter our Shop tab through: <a href="https://www.tiktok.com/@sevenboxstore">SevenBox TikTok Shop</a></p>
<p><b>Can’t request samples?</b><br>We know you may not be able to request products directly through the TikTok portal. SevenBox is willing to offer you free samples and ship them to your address directly.</p>
<p>
<b>What you get from us:</b>
<ul>
  <li>1-2 Free samples</li>
  <li>15-20% Commission</li>
</ul>
</p>
<p>
<b>What we expect from you:</b>
<ul>
  <li>Add product to showcase</li>
  <li>Post your content within 7 days of receiving</li>
</ul>
</p>
<p><mark>Please reply with the products you’re interested in, along with your shipping address.</mark><br>Full Name:<br>Address:<br>Phone:<br></p>
<p>Best Regards,<br>Rena | Chief Executive Officer<br>SevenBox LLC <a href="https://www.tiktok.com/@sevenboxstore">@sevenboxstore</a></p>
</body>
</html>'''.replace("[@handle]", name)

    def get_html_content_3(self, name: str):
        return '''<div dir=3D"ltr"><div dir=3D"ltr"><div>Dear [@handle],</div><div><br></div>=
<div>You=E2=80=99ve been selected for a personalized collaboration invite f=
rom @sevenboxstore. Enter our Shop tab through: <a href=3D"https://www.tikt=
ok.com/@sevenboxstore">https://www.tiktok.com/@sevenboxstore</a></div><div>=
<br></div><div><b>Can=E2=80=99t request samples?</b></div><div>We know you =
may not be able to request products directly through the TikTok portal. Sev=
enBox is willing to offer you free samples and ship them to your address di=
rectly.</div><div><b><br></b></div><div><b>What you get from us:</b></div><=
div>=E2=80=A2<span style=3D"white-space:pre">=09</span>1-2 Free samples</di=
v><div>=E2=80=A2<span style=3D"white-space:pre">=09</span>15-20% Commission=
</div><div><b>What we expect from you:</b></div><div>=E2=80=A2<span style=
=3D"white-space:pre">=09</span>Add product to showcase</div><div>=E2=80=A2<=
span style=3D"white-space:pre">=09</span>Post your content within 7 days of=
 receiving=C2=A0</div><div><br></div><div><span style=3D"background-color:r=
gb(255,255,0)">Please reply with the products you=E2=80=99re interested in,=
 along with your shipping address.=C2=A0</span></div><div>Full Name:<span s=
tyle=3D"white-space:pre">=09</span></div><div>Address:<span style=3D"white-=
space:pre">=09</span></div><div>Phone:<span style=3D"white-space:pre">=09</=
span></div><div><br></div><div><br></div><div>Best Regards,=C2=A0</div><div=
><img src=3D"cid:ii_luvuuxgr7" alt=3D"image.png" width=3D"468" height=3D"75=
" style=3D"margin-right: 0px;"><br></div></div></div>'''.replace("[@handle]", name)


# if __name__ == "__main__":
#     emailPlugin = EmailPlugin()
#     emailPlugin.send_email_brevo(recipient_name="abc", recipient_email="30000eric@gmail.com")
