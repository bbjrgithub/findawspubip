package main

import (
	"context"
	"fmt"
	"log"
	"net"
	"os"

	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/ec2"
)

func main() {
	if len(os.Args) != 2 {
		fmt.Println("No input. Please enter an IP address")
		return
	}

	// Check if entered IP is a valid IP address
	pubIPAddress := os.Args[1]

	if len(os.Args[1]) > 0 {
		if net.ParseIP(pubIPAddress) == nil {
			fmt.Println("Value is not a valid IP address.")
		} else {
			fmt.Println("Entered IP Address:", pubIPAddress)
		}
	}

	cfg, err := config.LoadDefaultConfig(context.TODO())
	if err != nil {
		log.Fatalf("Unable to load AWS SDK config, %v", err)
	}

	ec2Client := ec2.NewFromConfig(cfg)

	// Get available regions in the account
	availableRegions, err := ec2Client.DescribeRegions(context.TODO(), &ec2.DescribeRegionsInput{})
	if err != nil {
		log.Fatalf("Unable to get AWS regions, %v", err)
	}

	foundIP := true

	fmt.Println("\n...Searching regions for IP")
out:
	for _, region := range availableRegions.Regions {
		fmt.Println("\nSearching for IP in", *region.RegionName)

		ec2Client := ec2.NewFromConfig(cfg, func(o *ec2.Options) {
			o.Region = (*region.RegionName)
		})

		// Get list of up to 1,000 network interfaces per page
		describeIntefacesPaginator := ec2.NewDescribeNetworkInterfacesPaginator(ec2Client, &ec2.DescribeNetworkInterfacesInput{}, func(o *ec2.DescribeNetworkInterfacesPaginatorOptions) {
			o.Limit = 1000
		})

		// Loop through available pages of network interfaces
		for describeIntefacesPaginator.HasMorePages() {
			output, err := describeIntefacesPaginator.NextPage(context.TODO())
			if err != nil {
				fmt.Println("Error", err)
				break
			}

			// For each network interface if it has an Association it has a public IP.
			// Checkf if IP is the one that was entered
			for _, netInterface := range output.NetworkInterfaces {

				if netInterface.Association != nil {

					if *netInterface.Association.PublicIp == pubIPAddress {
						fmt.Println("\nIP", pubIPAddress, "Found")
						fmt.Println("\nENI: ", *netInterface.NetworkInterfaceId, " PrivateIP: ", *netInterface.PrivateIpAddress, " PublicIP: ", *netInterface.Association.PublicIp)

						foundIP = true
						break out
					}

				}

			}

		}
	}

	if !foundIP {
		fmt.Println("\nPublic IP was not found")
	}

}
