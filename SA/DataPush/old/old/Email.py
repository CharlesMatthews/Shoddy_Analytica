import requests
import os


class Notify:
	def __init__(self,RecipientEmail,SiteLink,DriveLink):
		self.RecipientEmail = RecipientEmail
		self.SiteLink = SiteLink
		self.DriveLink = DriveLink
		self.MailGunKey = os.getenv("MAILGUN_KEY")
		self.MailGunSandbox = os.getenv("MAILGUN_SANDBOX")

	def send_mail(self):
		request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(self.MailGunSandbox)
		request = requests.post(request_url, auth=('api', self.MailGunKey), data={
				'from': 'KingPush@charlesmatthews.github.io',
				'to': self.RecipientEmail,
				'subject': 'Data request',
				'text': 'Hello there!\n You should be able to access the scraped data on the site here:  {0} \n\n Alternatively you can view and download the raw data from google sheets here:\n\n  {1}'.format(self.SiteLink,self.DriveLink)
		})

		print ('Status: {0}'.format(request.status_code))
		print ('Body:   {0}'.format(request.text))



	#https://www.campaignmonitor.com/email-templates/


