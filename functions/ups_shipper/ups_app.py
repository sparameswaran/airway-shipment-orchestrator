import json
import uuid
import os
import time

import requests
import requests.auth

# Only for testing
# Needs also valid shipper number that needs to be same for payment information account number
CLIENT_ID = "EDIT_ME_TEST_CLIENT_ID"
CLIENT_SECRET = "EDIT_ME_TEST_CLIENT_SECRET"
REDIRECT_URI = "https://wwwcie.ups.com/api"

USE_SIMULATOR = os.getenv('SIMULATE')

def get_token(code):
	try:
		client_auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
		post_data = {"grant_type": "client_credentials"}
		response = requests.post("https://wwwcie.ups.com/security/v1/oauth/token",
								auth=client_auth,
								data=post_data)
		token_json = response.json()
		print('Token json: ', token_json)
		return token_json["access_token"]
	except Exception as e:
		print(e)

def reprint_label(auth_token):
	try:
		header = {
					'Authorization': 'Bearer ' + auth_token,
					'Content-Type': 'application/json',
					'transactionSrc': 'testing',
					'accept': 'application/json'
				}
		data = {
            "LabelRecoveryRequest": {
              "Request": {
                "RequestOption": "Non_Validate",
                "SubVersion": "1903",
                "TransactionReference": {
                  "CustomerContext":"",
                  "TransactionIdentifier": ""
                }
              },
              "LabelSpecification": {
                "HTTPUserAgent": "Mozilla/4.5",
                "LabelImageFormat": {
                  "Code": "ZPL"
                },
                "LabelStockSize": {
                  "Height": "6",
                  "Width": "4"
                }
              },
              "Translate": {
                "LanguageCode": "eng",
                "DialectCode": "US",
                "Code": "01"
              },
              "LabelDelivery": {
                "LabelLinkIndicator": "",
                "ResendEmailIndicator": ""
              },
              "TrackingNumber": str(uuid.uuid4()).replace('-', '').upper()
            }
          }

		url = 'https://wwwcie.ups.com/api//labels/v1/recovery'
		response = requests.post(url, json=data, headers=header)
		return response
	except Exception as e:
		print(e)

def shipping_label(auth_token):
	try:
		header = {
					'Authorization': 'Bearer ' + auth_token,
					'Content-Type': 'application/json',
					'transactionSrc': 'testing',
					'accept': 'application/json'
				}
		data = {
				"ShipmentRequest": {
					"Request": {
						"SubVersion": "1801",
						"RequestOption": "nonvalidate",
						"TransactionReference": {
							"CustomerContext": ""
						}
					},
					"Shipment": {
						"Description": "Ship WS test",
						"Shipper": {
							"Name": "ShipperName",
							"AttentionName": "ShipperZs Attn Name",
							"TaxIdentificationNumber": "123456",
							"Phone": {
								"Number": "1115554758",
								"Extension": " "
							},
							"ShipperNumber": "3R5W45",
							"FaxNumber": "8002222222",
							"Address": {
								"AddressLine": "2311 York Rd",
								"City": "Timonium",
								"StateProvinceCode": "MD",
								"PostalCode": "21093",
								"CountryCode": "US"
							}
						},
						"ShipTo": {
							"Name": "Happy Dog Pet Supply",
							"AttentionName": "1160b_74",
							"Phone": {
								"Number": "9225377171"
							},
							"Address": {
								"AddressLine": "123 Main St",
								"City": "timonium",
								"StateProvinceCode": "MD",
								"PostalCode": "21030",
								"CountryCode": "US"
							},
							"Residential": " "
						},
						"ShipFrom": {
							"Name": "T and T Designs",
							"AttentionName": "1160b_74",
							"Phone": {
								"Number": "1234567890"
							},
							"FaxNumber": "1234567890",
							"Address": {
								"AddressLine": "2311 York Rd",
								"City": "Alpharetta",
								"StateProvinceCode": "GA",
								"PostalCode": "30005",
								"CountryCode": "US"
							}
						},
						"PaymentInformation": {
							"ShipmentCharge": {
								"Type": "01",
								"BillShipper": {
									"AccountNumber": "3R5W45"
								}
							}
						},
						"Service": {
							"Code": "03",
							"Description": "Express"
						},
						"Package": {
							"Description": " ",
							"Packaging": {
								"Code": "02",
								"Description": "Nails"
							},
							"Dimensions": {
								"UnitOfMeasurement": {
									"Code": "IN",
									"Description": "Inches"
								},
								"Length": "10",
								"Width": "30",
								"Height": "45"
							},
							"PackageWeight": {
								"UnitOfMeasurement": {
									"Code": "LBS",
									"Description": "Pounds"
								},
								"Weight": "5"
							}
						}
					},
					"LabelSpecification": {
						"LabelImageFormat": {
							"Code": "GIF",
							"Description": "GIF"
						},
						"HTTPUserAgent": "Mozilla/4.5"
					}
				}
			}

		url = 'https://wwwcie.ups.com/api/shipments/v1/ship'
		response = requests.post(url, json=data, headers=header)
		print('Shipping response', response)
		print(response.json())
		return response.json()

	except Exception as e:
		print(e)

def simulatedResponse(event):
	trackingId = '1Z12345E' + str(uuid.uuid4()).replace('-','').upper()[1:11]

	shippingLabelResponse = {
		'ShipmentResponse': {
			'Response': {
				'ResponseStatus': {
					'Code': '1',
					'Description': 'Success'
				},
				'Alert': {
					'Code': '129001',
					'Description': 'Additional Handling has automatically been set on Package 1.'
				},
				'TransactionReference': {
					'CustomerContext': 'testing'
				}
			},
			'ShipmentResults': {
				'ShipmentCharges': {
					'TransportationCharges': {
						'CurrencyCode': 'USD',
						'MonetaryValue': '76.49'
					},
					'ServiceOptionsCharges': {
						'CurrencyCode': 'USD',
						'MonetaryValue': '17.50'
					},
					'TotalCharges': {
						'CurrencyCode': 'USD',
						'MonetaryValue': '93.99'
					}
				},
				'BillingWeight': {
					'UnitOfMeasurement': {
						'Code': 'LBS',
						'Description': 'Pounds'
					},
					'Weight': '98.0'
				},
				'ShipmentIdentificationNumber': trackingId,
				'PackageResults': {
					'TrackingNumber': trackingId,
					'BaseServiceCharge': {
						'CurrencyCode': 'USD',
						'MonetaryValue': '62.83'
					},
					'ServiceOptionsCharges': {
						'CurrencyCode': 'USD',
						'MonetaryValue': '17.50'
					},
					'ShippingLabel': {
						'ImageFormat': {
							'Code': 'GIF',
							'Description': 'GIF'
						},
						'GraphicImage': 'R0lGODlheAUgA/cAAAAAAAEBAQI1tpvGRBd2slKbWzwG95mAVjWZJ1zPJzrz',
						'HTMLImage': 'PCFET0NUWVBFIEhUTUwgUFVCTEl+CjwvaHRtbD4K'
					},
					'ItemizedCharges': [{
						'Code': '432',
						'CurrencyCode': 'USD',
						'MonetaryValue': '0.00'
					}, {
						'Code': '100',
						'CurrencyCode': 'USD',
						'MonetaryValue': '17.50'
					}, {
						'Code': '376',
						'CurrencyCode': 'USD',
						'MonetaryValue': '0.00',
						'SubType': 'Suburban'
					}, {
						'Code': '375',
						'CurrencyCode': 'USD',
						'MonetaryValue': '13.66'
					}]
				}
			}
		}
	}
	response = {
                "UPSShipmentTrackingCode": shippingLabelResponse['ShipmentResponse']['ShipmentResults']['ShipmentIdentificationNumber'],
                "UPSShipmentTracker":  shippingLabelResponse,
                "ShipmentRequest": event
              }
	return response


token = get_token(1)

def lambda_handler(event, context):
    global token
    if USE_SIMULATOR is not None or USE_SIMULATOR == 'True':
    	return simulatedResponse(event)


    print('Incoming event: ', event)

    attempts = 1
    while token is None and attempts < 10:
      token = get_token(1)
      attempts += 1
      time.sleep(1)

    if token is None and attempts == 10:
      print('Could not obtain valid UPS Access Token after 10 attempts, aborting!!')
      raise Exception("Error! Could not obtain valid UPS Access Token after 10 attempts, aborting!!")

    shippingLabelResponse = shipping_label(token)

    if shippingLabelResponse is None:
      print('Could not obtain valid UPS shipping response, going with dummy response!!')
      #return { "Error": "Could not obtain valid UPS shipping response, aborting!!" }
      shippingLabelResponse = {
						'ShipmentResponse': {
							'Response': {
								'ResponseStatus': {
									'Code': '1',
									'Description': 'Success'
								},
								'Alert': {
									'Code': '129001',
									'Description': 'Additional Handling has automatically been set on Package 1.'
								},
								'TransactionReference': {
									'CustomerContext': 'testing'
								}
							},
							'ShipmentResults': {
								'ShipmentCharges': {
									'TransportationCharges': {
										'CurrencyCode': 'USD',
										'MonetaryValue': '76.49'
									},
									'ServiceOptionsCharges': {
										'CurrencyCode': 'USD',
										'MonetaryValue': '17.50'
									},
									'TotalCharges': {
										'CurrencyCode': 'USD',
										'MonetaryValue': '93.99'
									}
								},
								'BillingWeight': {
									'UnitOfMeasurement': {
										'Code': 'LBS',
										'Description': 'Pounds'
									},
									'Weight': '98.0'
								},
								'ShipmentIdentificationNumber': '1ZDUMMYIXXXXXXXXXX',
								'PackageResults': {
									'TrackingNumber': '1ZXXXXXXXXXXXXXXXX',
									'BaseServiceCharge': {
										'CurrencyCode': 'USD',
										'MonetaryValue': '62.83'
									},
									'ServiceOptionsCharges': {
										'CurrencyCode': 'USD',
										'MonetaryValue': '17.50'
									},
									'ShippingLabel': {
										'ImageFormat': {
											'Code': 'GIF',
											'Description': 'GIF'
										},
										'GraphicImage': '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Fixp8iTKlChHsmxJ0SRImC5nNlxJ8+ZIlTZxitSp06NMnkJfBiWYcijSmz5PHlzKlOHRpFKn1iSosCTVrFq3Psz+yPUr2LBiIzot63Ms2qId1aIlq7JtVrNwMZrFutbuXJpRz+ZtWxdhWbo7+xImetVr4cSKEyJe7PgxZKddl0JGynbjZcWUK7uUy3lo5s8Sf24Wbdkz46iCQ5smDODw69aytzaebfv2zLcXVeOOiZdk7cJ8ewMNTLzn7+MLSdt9qjwn6ufSRwefbr1i9evapfO22H07RNbes/stDd6t5PPYk18v6nygePU1o8vXzr4+fqP598sevNs/f03dhxl5YfE1YID0BZhagcepxVZ8CxplnITKIVjhdA1iuCFXAK73HoYRUqdhhyBOyKFACi72m4f/kYgbewNeGKKKKJo2o43+MMaWI48lmjjRdxWKiN6OeWWGI341uraSbne9eFuM1SG54F899veklZxhmSWXwDVJ5I8SDrlakUb6N6V8SvZ11JcEbnllmSfCxmWVXS45p53EvZknn0TV9eee9iEIaJjlvYWmemrOJdN7iELl6GxRxplioIkq2qdUO4IIKaZrTtopqBoR+iePoY1aaVzDbXipoQKWySmDn3JXm4yogldnqFrFhhWLtub6la+/gnpqejmaSuiNP61K4YqIJQcrYNCKRmyw7bEqbG6UwlektNiW6C24flI7ZpKDXuuYefudK1avr/pKbqTU0rluuDGlKKCr9T5Wrb55jisrh/AK2mL+msxq5mxj3VLKb7PEzmtwv3rdu22+ESfGsMVdIuuvwhkKbCHEwiHsLsAjlpwxyCGjjBxeI6/s6csxZ/yxpWKq7CmpTp4ss2248hxSrxX/zO7OQxudJc1HA3uzmTlzlLTSSzIdNctUf2s11kgjquy+GG9HL1gbP91x1kRPXfZoeKKdlNdru50siWen1ba1xdoI9dtLy533wryRzXd4RQM+eG/xAdowpmBbSjfheimOtqp/N76c4JNb/pl4ox5cOY12o4j35aA9XvaraocONOenqy41wAQTPJbk542u6+E6r46z56p7NWnsuqd+u57/5m4zeRGCzpPDVO4Ne+1jMw7+vM7prp4R7883bj30rAvfppDmvni8UqcSL73ITrv5e/Y4+Qz8a9Wjnz7F8C++PffjP/p97y0ln+DyZr//4f/kx5L1sc99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',
										'HTMLImage': 'PCFET0NUWVBFIEhUTUwgUFVCTElDICItLy9JRVRGLy9EVEQgSFRNTCAzLjIvL0VOIj4KPGh0bWw+PGhlYWQ+PHRpdGxlPgpWaWV3L1ByaW50IExhYmVsPC90aXRsZT48bWV0YSBjaGFyc2V0PSJVVEYtOCI+PC9oZWFkPjxzdHlsZT4KICAgIC5zbWFsbF90ZXh0IHtmb250LXNpemU6IDgwJTt9CiAgICAubGFyZ2VfdGV4dCB7Zm9udC1zaXplOiAxMTUlO30KPC9zdHlsZT4KPGJvZHkgYmdjb2xvcj0iI0ZGRkZGRiI+CjxkaXYgY2xhc3M9Imluc3RydWN0aW9ucy1kaXYiPgo8dGFibGUgY2xhc3M9Imluc3RydWN0aW9ucy10YWJsZSIgbmFtZWJvcmRlcj0iMCIgY2VsbHBhZGRpbmc9IjAiIGNlbGxzcGFjaW5nPSIwIiB3aWR0aD0iNjAwIj48dHI+Cjx0ZCBoZWlnaHQ9IjQxMCIgYWxpZ249ImxlZnQiIHZhbGlnbj0idG9wIj4KPEIgY2xhc3M9ImxhcmdlX3RleHQiPlZpZXcvUHJpbnQgTGFiZWw8L0I+CiZuYnNwOzxicj4KJm5ic3A7PGJyPgo8b2wgY2xhc3M9InNtYWxsX3RleHQiPiA8bGk+PGI+UHJpbnQgdGhlIGxhYmVsOjwvYj4gJm5ic3A7ClNlbGVjdCBQcmludCBmcm9tIHRoZSBGaWxlIG1lbnUgaW4gdGhpcyBicm93c2VyIHdpbmRvdyB0byBwcmludCB0aGUgbGFiZWwgYmVsb3cuPGJyPjxicj48bGk+PGI+CkZvbGQgdGhlIHByaW50ZWQgbGFiZWwgYXQgdGhlIGRvdHRlZCBsaW5lLjwvYj4gJm5ic3A7ClBsYWNlIHRoZSBsYWJlbCBpbiBhIFVQUyBTaGlwcGluZyBQb3VjaC4gSWYgeW91IGRvIG5vdCBoYXZlIGEgcG91Y2gsIGFmZml4IHRoZSBmb2xkZWQgbGFiZWwgdXNpbmcgY2xlYXIgcGxhc3RpYyBzaGlwcGluZyB0YXBlIG92ZXIgdGhlIGVudGlyZSBsYWJlbC48YnI+PGJyPjxsaT48Yj5HRVRUSU5HIFlPVVIgU0hJUE1FTlQgVE8gVVBTPC9iPjxicj4KPGI+Q3VzdG9tZXJzIHdpdGggYSBEYWlseSBQaWNrdXA8L2I+PHVsPjxsaT4KWW91ciBkcml2ZXIgd2lsbCBwaWNrdXAgeW91ciBzaGlwbWVudChzKSBhcyB1c3VhbC4gPC91bD4KIDxicj4gCjxiPkN1c3RvbWVycyB3aXRob3V0IGEgRGFpbHkgUGlja3VwPC9iPjx1bD48bGk+VGFrZSB0aGlzIHBhY2thZ2UgdG8gYW55IGxvY2F0aW9uIG9mIFRoZSBVUFMgU3RvcmXDr8K/wr0sIFVQUyBEcm9wIEJveCwgVVBTIEN1c3RvbWVyIENlbnRlciwgVVBTIEFsbGlhbmNlcyAoT2ZmaWNlIERlcG90w6/Cv8K9IG9yIFN0YXBsZXPDr8K/wr0pIG9yIEF1dGhvcml6ZWQgU2hpcHBpbmcgT3V0bGV0IG5lYXIgeW91IG9yIHZpc2l0IDxhIGhyZWY9Imh0dHA6Ly93d3cudXBzLmNvbS9jb250ZW50L3VzL2VuL2luZGV4LmpzeCI+d3d3LnVwcy5jb20vY29udGVudC91cy9lbi9pbmRleC5qc3g8L2E+IGFuZCBzZWxlY3QgRHJvcCBPZmYuPGxpPgpBaXIgc2hpcG1lbnRzIChpbmNsdWRpbmcgV29ybGR3aWRlIEV4cHJlc3MgYW5kIEV4cGVkaXRlZCkgY2FuIGJlIHBpY2tlZCB1cCBvciBkcm9wcGVkIG9mZi4gVG8gc2NoZWR1bGUgYSBwaWNrdXAsIG9yIHRvIGZpbmQgYSBkcm9wLW9mZiBsb2NhdGlvbiwgc2VsZWN0IHRoZSBQaWNrdXAgb3IgRHJvcC1vZmYgaWNvbiBmcm9tIHRoZSBVUFMgdG9vbCBiYXIuICA8L3VsPjwvb2w+PC90ZD48L3RyPjwvdGFibGU+PHRhYmxlIGJvcmRlcj0iMCIgY2VsbHBhZGRpbmc9IjAiIGNlbGxzcGFjaW5nPSIwIiB3aWR0aD0iNjAwIj4KPHRyPgo8dGQgY2xhc3M9InNtYWxsX3RleHQiIGFsaWduPSJsZWZ0IiB2YWxpZ249InRvcCI+CiZuYnNwOyZuYnNwOyZuYnNwOwo8YSBuYW1lPSJmb2xkSGVyZSI+Rk9MRCBIRVJFPC9hPjwvdGQ+CjwvdHI+Cjx0cj4KPHRkIGFsaWduPSJsZWZ0IiB2YWxpZ249InRvcCI+PGhyPgo8L3RkPgo8L3RyPgo8L3RhYmxlPgoKPHRhYmxlPgo8dHI+Cjx0ZCBoZWlnaHQ9IjEwIj4mbmJzcDsKPC90ZD4KPC90cj4KPC90YWJsZT4KCjwvZGl2Pgo8dGFibGUgYm9yZGVyPSIwIiBjZWxscGFkZGluZz0iMCIgY2VsbHNwYWNpbmc9IjAiIHdpZHRoPSI2NTAiID48dHI+Cjx0ZCBhbGlnbj0ibGVmdCIgdmFsaWduPSJ0b3AiPgo8SU1HIFNSQz0iLi9sYWJlbDFaM1I1VzQ1MDMyNTIwODE1Ny5naWYiIGhlaWdodD0iMzkyIiB3aWR0aD0iNjUxIj4KPC90ZD4KPC90cj48L3RhYmxlPgo8L2JvZHk+CjwvaHRtbD4K'
									},
									'ItemizedCharges': [{
										'Code': '432',
										'CurrencyCode': 'USD',
										'MonetaryValue': '0.00'
									}, {
										'Code': '100',
										'CurrencyCode': 'USD',
										'MonetaryValue': '17.50'
									}, {
										'Code': '376',
										'CurrencyCode': 'USD',
										'MonetaryValue': '0.00',
										'SubType': 'Suburban'
									}, {
										'Code': '375',
										'CurrencyCode': 'USD',
										'MonetaryValue': '13.66'
									}]
								}
							}
						}
					}

    #shipping_print_response = reprint_label(token)
    #print('Shipping print label: ', shipping_print_response)

    response = {
                "UPSShipmentTrackingCode": shippingLabelResponse['ShipmentResponse']['ShipmentResults']['ShipmentIdentificationNumber'],
                "UPSShipmentTracker":  shippingLabelResponse,
                "ShipmentRequest": event
              }
    return response
