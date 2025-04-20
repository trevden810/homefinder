$(document).ready(function() {
    // Sample property data for demonstration
    const sampleProperties = [
        {
            id: "123abc",
            source: "zillow",
            url: "https://www.zillow.com/homedetails/123-main-st",
            address: "123 Main St",
            city: "Denver",
            state: "CO",
            zip_code: "80202",
            price: 450000,
            bedrooms: 3,
            bathrooms: 2,
            square_feet: 1800
        },
        {
            id: "456def",
            source: "realtor",
            url: "https://www.realtor.com/realestateandhomes-detail/456-oak-ave",
            address: "456 Oak Ave",
            city: "Denver",
            state: "CO",
            zip_code: "80203",
            price: 525000,
            bedrooms: 4,
            bathrooms: 2.5,
            square_feet: 2200
        },
        {
            id: "789ghi",
            source: "redfin",
            url: "https://www.redfin.com/CO/Denver/789-pine-blvd",
            address: "789 Pine Blvd",
            city: "Denver",
            state: "CO",
            zip_code: "80205",
            price: 375000,
            bedrooms: 2,
            bathrooms: 1,
            square_feet: 1200
        }
    ];
    
    // Handle form submission
    $('#searchForm').on('submit', function(e) {
        e.preventDefault();
        
        // Get selected sources
        const sources = [];
        $('input[name="sources"]:checked').each(function() {
            sources.push($(this).val());
        });
        
        // Check if at least one source is selected
        if (sources.length === 0) {
            alert('Please select at least one source.');
            return;
        }
        
        // Prepare the search data
        const searchData = {
            location: $('#location').val(),
            minPrice: parseFloat($('#minPrice').val()),
            maxPrice: parseFloat($('#maxPrice').val()),
            bedrooms: parseFloat($('#bedrooms').val()),
            bathrooms: parseFloat($('#bathrooms').val()),
            sources: sources
        };
        
        // Show loading indicator
        $('#loadingIndicator').show();
        
        // Hide previous results
        $('#results').hide();
        
        // Disable export buttons
        $('#exportCsv, #exportJson').prop('disabled', true);
        
        // Simulate API call - in a real app, this would call your backend
        setTimeout(function() {
            // Hide loading indicator
            $('#loadingIndicator').hide();
            
            // Filter sample properties based on search criteria
            const filteredProperties = sampleProperties.filter(function(property) {
                let match = true;
                
                // Filter by price
                if (property.price < searchData.minPrice || property.price > searchData.maxPrice) {
                    match = false;
                }
                
                // Filter by bedrooms
                if (property.bedrooms < searchData.bedrooms) {
                    match = false;
                }
                
                // Filter by bathrooms
                if (property.bathrooms < searchData.bathrooms) {
                    match = false;
                }
                
                // Filter by source
                if (!searchData.sources.includes(property.source)) {
                    match = false;
                }
                
                return match;
            });
            
            // Update result count
            $('#resultCount').text(filteredProperties.length);
            
            // Clear previous results
            $('#propertiesContainer').empty();
            
            // Display properties
            if (filteredProperties.length > 0) {
                displayProperties(filteredProperties);
                
                // Enable export buttons
                $('#exportCsv, #exportJson').prop('disabled', false);
            } else {
                $('#propertiesContainer').html('<div class="col-12"><p>No properties found matching your criteria.</p></div>');
            }
            
            // Show results
            $('#results').show();
        }, 1500); // Simulate network delay
    });
    
    // Handle export buttons
    $('#exportCsv').on('click', function() {
        alert('In a full version, this would export to CSV.');
    });
    
    $('#exportJson').on('click', function() {
        alert('In a full version, this would export to JSON.');
    });
    
    // Function to display properties
    function displayProperties(properties) {
        properties.forEach(function(property) {
            // Format price
            const price = new Intl.NumberFormat('en-US', {
                style: 'currency',
                currency: 'USD',
                maximumFractionDigits: 0
            }).format(property.price);
            
            // Create card
            const card = `
                <div class="col-md-4">
                    <div class="card property-card">
                        <div class="card-body">
                            <span class="property-source">${property.source.charAt(0).toUpperCase() + property.source.slice(1)}</span>
                            <h5 class="card-title">${property.address}</h5>
                            <h6 class="card-subtitle mb-2 text-muted">${property.city}, ${property.state} ${property.zip_code}</h6>
                            <p class="card-text price">${price}</p>
                            <p class="card-text">
                                <strong>Beds:</strong> ${property.bedrooms} &nbsp; 
                                <strong>Baths:</strong> ${property.bathrooms}
                                ${property.square_feet ? `&nbsp; <strong>Sqft:</strong> ${Math.round(property.square_feet).toLocaleString()}` : ''}
                            </p>
                            <a href="${property.url}" class="btn btn-sm btn-outline-primary" target="_blank">View on ${property.source.charAt(0).toUpperCase() + property.source.slice(1)}</a>
                        </div>
                    </div>
                </div>
            `;
            
            // Add to container
            $('#propertiesContainer').append(card);
        });
    }
});
