// If the Lambda function is installed in a master payer account, it will
// list all accounts and inventory each one using the OrganizationAccessRole
// if accounts_info = ""
module "example_master" {
  accounts_info = ""
  source_file   = "../release/inventory-lambda.zip"
  appenv        = "production"
  project_name  = "allcloud"
}
