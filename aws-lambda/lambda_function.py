import xlsxwriter, boto3, datetime


regions = ['us-east-1', 'us-east-2']

no_region_resources = {}
all_resources = {}

for region in regions:
    all_resources[region] = {}


def lambda_handler(event=None, context=None):
    def resrc_func():
        ###..For S3..
        s3_resource = boto3.client('s3')
        bucket_response = s3_resource.list_buckets()
        buckets = bucket_response.get('Buckets', [])
        if (len(buckets) != 0):
            s3 = []
            for bucket in buckets:
                if not bucket['Name'].startswith("ahad"):
                    s3.append(bucket['Name'])
                no_region_resources["s3"] = s3
            print("______S3 bucket found______")
        else:
            print("______No S3 bucket found______")
        for region in regions:

            ###..EC2..
            ec2_resource = boto3.client('ec2', region_name = region)
            ec2_response = ec2_resource.describe_instances()
            ec2_instances = ec2_response.get('Reservations', [])
            if (len(ec2_instances) != 0):
                ec2_lst = []
                for reservation in ec2_response["Reservations"]:
                    for instance in reservation["Instances"]:
                        try:
                            instance['Tags']
                            for i in range(len(instance['Tags'])):
                                if instance['Tags'][i]['Key'] == "Name":
                                    if instance['Tags'][i]['Value'] == '':
                                        id = instance["InstanceId"]
                                        ec2_lst.append(f"InstanceId {id}")
                                    else:
                                        ec2_lst.append(instance['Tags'][i]['Value'])
                        except KeyError:
                            for instance in reservation["Instances"]:
                                id = instance["InstanceId"]
                                ec2_lst.append(f"InstanceId {id}")
                for key, value in all_resources.items():
                    if key == region:
                        value = all_resources[region]
                        value['ec2'] = ec2_lst
                    print("______EC2 Instance found______")
                else:
                    print("______No EC2 Instance found______")

            ###..Lambda_Function..
            lambda_resource = boto3.client('lambda', region_name = region)
            lambda_response = lambda_resource.list_functions()
            lambda_instances = lambda_response.get('Functions', [])
            if (len(lambda_instances) != 0):
                lmbda = []
                for function in lambda_response['Functions']:
                    lmbda.append(function['FunctionName'])
                for key, value in all_resources.items():
                    if key == region:
                        value = all_resources[region]
                        value['lambda'] = lmbda
                print("______Lambda Function found______")
            else:
                print("______No Lambda Function found______")

            ### RDS Instance

            db_client = boto3.client('rds', region_name = region)
            db_instances = db_client.describe_db_instances()
            if (len(db_instances) != 0):
                RDS = []
                for i in range(len(db_instances)):
                    print(db_instances)
                    j = i - 1
                    try:
                        DBName = db_instances['DBInstances'][j]['DBName']
                        if DBName:
                            RDS.append(DBName)
                        # MasterUsername = db_instances['DBInstances'][0]['MasterUsername']
                        # DBInstanceClass = db_instances['DBInstances'][0]['DBInstanceClass']
                        # DBInstanceIdentifier = db_instances['DBInstances'][0]['DBInstanceIdentifier']
                        # Endpoint = db_instances['DBInstances'][0]['Endpoint']
                        # Address = db_instances['DBInstances'][0]['Endpoint']['Address']
                        for key, value in all_resources.items():
                            if key == region:
                                value = all_resources[region]
                                value['RDS'] = RDS
                    except (KeyError, IndexError) as e:
                        continue

    today = datetime.datetime.today().strftime("%d-%b-%Y")

    def excel_file():
        workbook = xlsxwriter.Workbook(f'/tmp/AWS_Resources_list_{today}.xlsx')
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format(
            {'bold': True, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#6AD9F7'})
        merge_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#E8E5E5',
        })
        center_format = workbook.add_format({
            'bold': False,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'shrink': 'true'
        })

        i = 0
        row = 1
        col = 0

        while (i < len(no_region_resources)):
            worksheet.set_column(row, col, 25)
            worksheet.write(row, col, "Resource name", bold)
            worksheet.write(row, col + 1, "Count", bold)
            for key, value in no_region_resources.items():
                worksheet.write(row + 1, col, key, merge_format)
                worksheet.write(row + 1, col + 1, len(value), merge_format)
                row += 1
                i += 1

        col = 3
        j = 0

        while (j < len(no_region_resources)):
            for key, value in no_region_resources.items():
                row = 0
                worksheet.write(row + 1, col + j, key, merge_format)
                for v in value:
                    worksheet.write(row + 2, col + j, v, center_format)
                    row += 1
                j += 1

        col += len(no_region_resources)
        COLL = chr(ord('@') + col)

        worksheet.merge_range(f'A1:{COLL}1', 'Not region specific', bold)
        worksheet.set_column(f'A1:{COLL}1', 15)
        worksheet.write(0, 0, "Not region specific resources", bold)

        row = worksheet.dim_rowmax
        row += 3

        worksheet.merge_range(f'A{row}:{COLL}{row}', 'Region specific', bold)
        worksheet.write(f'A{row}', 'Region specific resources', bold)

        for region in regions:
            i = 0
            resource_row = row
            row += 1
            try:
                all_resources[region] and len(all_resources.values())
                worksheet.merge_range(f'A{row}:{COLL}{row}', 'Region specific', bold)
                worksheet.write(f'A{row}', region, bold)
            except KeyError:
                continue
            col = 0
            for key in all_resources.keys():
                if key == region:
                    value = all_resources[key]
                    while (i < len(value)):
                        worksheet.write(row, col, "Resource name", merge_format)
                        worksheet.write(row, col + 1, "No of resources", merge_format)
                        for key, values in value.items():
                            worksheet.write(row + 1, col, key, merge_format)
                            worksheet.write(row + 1, col + 1, len(values), merge_format)
                            row += 1
                            i += 1

                    j = 0
                    col = 3

                    while (j < len(value)):
                        if type(value) == 'dict':
                            for key, value in value.items():
                                worksheet.write(resource_row + 1, col + j, key, merge_format)
                                # for v in value:
                                #     worksheet.write(resource_row + 2, col + j, v, center_format)
                                #     resource_row += 1
                        j += 1

            col += len(all_resources.values())
            row = worksheet.dim_rowmax
            row += 2

        workbook.close()
        print(f"______Excel file: AWS_Resources_list_{today}.xlsx is created______")

    def upload_file():
        s3_client = boto3.resource('s3')
        s3_client.Bucket('fas-test-inventory').upload_file(Filename=f'/tmp/AWS_Resources_list_{today}.xlsx',
                                                                    Key=f'resources/AWS_Resources_list_{today}.xlsx')
        print("______Uploaded file to s3 bucket: ahad-test-3______")

    # def sns ():
    #     sns_client = boto3.client('sns')
    #     sns_message = str(f"Please check the Excel file and delete unnecessary resources. It helps us to reduce AWS cost. \n\n File path: s3://ahad-test-3/resources/AWS_Resources_list_{today}.xlsx \n\n Thank you.")
    #     subject= "AWS Resource list"
    #     sns_client.publish(
    #             TopicArn='arn:aws:sns:ap-northeast-1:450454010996:test-sns-lambda',
    #             Message= str(sns_message),
    #             Subject= str(subject)
    #     )
    #     print ("______Email sent______")
    resrc_func()
    excel_file()
    upload_file()


#   sns()

lambda_handler()