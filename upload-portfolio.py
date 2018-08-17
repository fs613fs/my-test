import boto3
import StringIO
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-east-1:930720100739:deployPortfolioTopic')

    try:
        s3 = boto3.resource('s3')

        build_bucket = s3.Bucket('portfoliobuild.feisun.me')
        portfolio_bucket = s3.Bucket('feisun.me')

        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('buildfeisun.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm, ExtraArgs={'ContentType': mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')
        print 'Job done'
        topic.publish(Subject="Portfolio Deployed", Message="Portfolio Deployed Successfully")
    except Exception, e:
        topic.publish(Message="Portfolio Deployment Failed",Subject="Portfolio Deployment Failed")
        raise e
