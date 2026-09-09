/* =====================================
All JavaScript fuctions Start
======================================*/
(function ($) {
	
    'use strict';
/*--------------------------------------------------------------------------------------------
	document.ready ALL FUNCTION START
---------------------------------------------------------------------------------------------*/	

	// Wow Animate function by = owl.js
    function wow_animate(){    	
		var wow = new WOW(
		  {
			boxClass:     'wow', 
			animateClass: 'animated',
			offset:0,    
			mobile: true,      
			live:true,   
			scrollContainer: null 
		  }
		);
		wow.init();
	}
	

// testimonial One Carousel Onefunction by = owl.js **************************************************
    function aon_testi_one(){    
        jQuery('.aon-testi-one-carousel').owlCarousel({
            loop:true,
            margin:30,
            center:true,
            nav:false,
            dots: true,
            navText: ['<i class="feather-chevron-left"></i>', '<i class="feather-chevron-right"></i>'],
            responsive:{
                0:{
                    items:1,
                    center:false,
                },
                991:{
                    items:2,
					center:false,
                },
                1200:{
                    items:3,
					center:false,
                }
            }
        });
    }    
	
// Case Studies Carousel Onefunction by = owl.js **************************************************
    function aon_case_studies(){    
        jQuery('.mos-case-studies-carousel').owlCarousel({
            loop:true,
            margin:30,
            center:false,
            nav:false,
            dots: true,
            navText: ['<i class="feather-chevron-left"></i>', '<i class="feather-chevron-right"></i>'],
            responsive:{
                0:{
                    items:1,
                },
                767:{
                    items:2,
                },
                991:{
                    items:3,
                },
                1280:{
                    items:4,
                }
            }
        });
    }  	
	
	
// Lates Discover Carousel function by = owl.js **************************************************
    function aon_lates_discover(){    
        jQuery('.mos-lates-discover').owlCarousel({
            loop:true,
            margin:30,
            center:true,
            nav:false,
            dots: true,
            navText: ['<i class="feather-chevron-left"></i>', '<i class="feather-chevron-right"></i>'],
            responsive:{
                0:{
                    items:1,
                    center:false,
                },
                991:{
                    items:2,
					center:false,
                },
                1024:{
                    items:3,
					center:false,
                },
                1280:{
                    items:4,
					center:false,
                }
            }
        });
    }      
	
// Features CarouselCarousel function by = owl.js **************************************************
    function aon_features_carousel(){    
        jQuery('.mos-features-carousel').owlCarousel({
            loop:true,
            margin:18,
            center:false,
            nav:true,
            dots: false,
            navText: ['<i class="feather-chevron-left"></i>', '<i class="feather-chevron-right"></i>'],
            responsive:{
                0:{
                    items:1,
                },
                767:{
                    items:2,
                },
                991:{
                    items:3,
                },
                1280:{
                    items:4,
                }
            }
        });
    }     	
	
    
    
	/*Submot contact form*/
	jQuery(document).on('submit', 'form.contact-form', function(e){
		e.preventDefault();
		var form = jQuery(this);
		/* sending message */
		jQuery.ajax({
			url: 'https://aonetheme.com/tranel/contact-form.php',
			data: form.serialize() + "&action=contactform",
			type: 'POST',
			dataType: 'JSON',
			beforeSend: function() {
				jQuery('.alert').remove();
				jQuery('.loading-area').show();
			},
			success:function(data){
				jQuery('.loading-area').hide();
				if(data['success']){
				jQuery("<div class='alert alert-success'>"+data['message']+"</div>").insertBefore('form.contact-form');
				jQuery('.alert-success').delay(20000).fadeOut(500);
				}else{
				jQuery("<div class='alert alert-danger'>"+data['message']+"</div>").insertBefore('form.contact-form');
				}
			}
		});
	});	
	
// Header Search Popup function by = custom.js ========================= //	
	function header_search_popup() {	
	   jQuery('.aon-btn-search, .aon-seach-close').on('click', function() { 
		  jQuery('body').toggleClass('active-search');
	   });  
	  } 
    
    
// Video responsive function by = custom.js ========================= //	
	function video_responsive(){	
		jQuery('iframe[src*="youtube.com"]').wrap('<div class="embed-responsive embed-responsive-16by9"></div>');
		jQuery('iframe[src*="vimeo.com"]').wrap('<div class="embed-responsive embed-responsive-16by9"></div>');	
	}
    
    
	 // Banner Home 1 Full Width Slide function by = owl.carousel.js **************************************************************
	function aon_bnr1_carousal(){
		jQuery('.aon-bnr1-carousal').owlCarousel({
			rtl: false,
			loop:true,
			navigation: true,
			slideSpeed: 300,
			paginationSpeed: 400,
			autoPlay: true,
			items:1,
			nav:true,
			dots: false,
		   mouseDrag: false,
			animateIn: 'fadeIn',
			animateOut: 'fadeOut',
			navText: ['<i class="feather-chevron-left"></i>', '<i class="feather-chevron-right"></i>']
		})
	}  	
	
	
	
	
	 // Banner Home 2 Full Width Slide function by = owl.carousel.js **************************************************************
	function aon_bnr2_carousal(){
		jQuery('.aon-bnr2-carousal').owlCarousel({
			rtl: false,
			loop:true,
			navigation: true,
			slideSpeed: 300,
			paginationSpeed: 400,
			autoPlay: true,
			items:1,
			nav:true,
			dots: false,
		    mouseDrag: false,
			animateIn: 'fadeIn',
			animateOut: 'fadeOut',
			navText: ['<i class="feather-chevron-left"></i>', '<i class="feather-chevron-right"></i>']
		})
	}  		
	
	// Banner Home 3 Full Width Slide function by = owl.carousel.js **********************
	 function aon_bnr3_carousal(){
		jQuery('.aon-bnr3-carousal').owlCarousel({
			rtl: false,
			loop:true,
			navigation: true,
			slideSpeed: 300,
			paginationSpeed: 400,
			autoPlay: true,
			items:1,
			nav:true,
			dots: false,
		   mouseDrag: false,
			animateIn: 'fadeIn',
			animateOut: 'fadeOut',
			navText: ['<i class="feather-chevron-left"></i>', '<i class="feather-chevron-right"></i>']
		})
	}       
	

//  Service List function by = owl.js *********************************************************
	function mos_service_carousel(){    
		jQuery('.mos-service-carousel').owlCarousel({
			loop:true,
			margin:20,
			items:3,
			nav:false,
			dots: true,
			navText: ['<i class="fa flaticon-031-arrow-1"></i>', '<i class="flaticon-030-arrow"></i>'],
			responsive:{
                0:{
                    items:1,
                    center:false,
                },
                575:{
                    items:2,
                },
				991:{
                    items:3,
                },
                1024:{
                    items:4,
                },
                1200:{
                    items:6,
                }
            }
		});
	}
	
	
    //  Our Expart Team Function by = owl.js *********************************************************
	function mos_team_carousel(){    
		jQuery('.mos-team-carousel').owlCarousel({
			loop:true,
			margin:0,
			items:3,
			nav:false,
			dots: true,
			navText: ['<i class="fa flaticon-031-arrow-1"></i>', '<i class="flaticon-030-arrow"></i>'],
			responsive:{
                0:{
                    items:1,
                    center:false,
                },
                767:{
                    items:2,
                },
				991:{
                    items:3,
                },
                1024:{
                    items:4,
                }
            }
		});
	}	
	
    //  Our Expart Team 2 Function by = owl.js *********************************************************
	function mos_team2_carousel(){    
		jQuery('.mos-team2-carousel').owlCarousel({
			loop:true,
			margin:24,
			items:1,
			nav:false,
			dots: true,
			navText: ['<i class="fa flaticon-031-arrow-1"></i>', '<i class="flaticon-030-arrow"></i>'],
			responsive:{
                0:{
                    items:1,
                    center:false,
                },
                767:{
                    items:2,
                },
				1024:{
                    items:3,
                }
            }
		});
	}	
	
//  Our Expart Team 3 Function by = owl.js ************************************************
	function mos_team3_carousel(){    
		jQuery('.mos-team3-carousel').owlCarousel({
			loop:true,
			margin:15,
			items:3,
			nav:false,
			dots: true,
			navText: ['<i class="fa flaticon-031-arrow-1"></i>', '<i class="flaticon-030-arrow"></i>'],
			responsive:{
				0:{
					items:1,
					center:false,
				},
				767:{
					items:2,
				},
				991:{
					items:3,
				},
				1200:{
					items:4,
				}
			}
		});
	}	
	
  //  Our Solutions Function by = owl.js *********************************************************
	function mos_solutions_carousel(){    
		jQuery('.mos-solutions-carousel').owlCarousel({
			loop:true,
			margin:24,
			items:1,
			nav:true,
			dots: false,
			navText: ['<i class="feather-chevron-left"></i>', '<i class="feather-chevron-right"></i>'],
		});
	}	
	
	
//  Latest News Function by = owl.js *********************************************************
	function mos_news_carousel(){    
		jQuery('.mos-news-carousel').owlCarousel({
			loop:true,
			margin:25,
			items:3,
			nav:false,
			dots: true,
			navText: ['<i class="fa flaticon-031-arrow-1"></i>', '<i class="flaticon-030-arrow"></i>'],
			responsive:{
                0:{
                    items:1,
                    center:false,
                },
                767:{
                    items:2,
                },
				991:{
                    items:3,
                },
                1024:{
                    items:4,
                }
            }
		});
	}	
	
	
	
	// video title  Carousel function by = owl.js *************************************************
	function video_title_slider(){    
		jQuery('.video-title-slider').owlCarousel({
			loop:true,
			margin:30,
			items:1,
			nav:false,
			dots: true,
			navText: ['<i class="fa flaticon-031-arrow-1"></i>', '<i class="flaticon-030-arrow"></i>'],
			responsive:{
                0:{
                    items:1,
                },
                767:{
                    items:1,
                },
                1024:{
                    items:1,
                }
            }
		});
	}	
	
	
 // > LIGHTBOX Gallery Popup function	by = lc_lightbox.lite.js =========================== //      
 	function lightbox_popup(){
        lc_lightbox('.elem', {
            wrap_class: 'lcl_fade_oc',
            gallery : true,	
            thumb_attr: 'data-lcl-thumb', 
            
            skin: 'minimal',
            radius: 0,
            padding	: 0,
            border_w: 0,
        });
	}			
// > magnificPopup for video function	by = magnific-popup.js ===================== //	
	function magnific_video(){	
		jQuery('.mfp-video').magnificPopup({
			type: 'iframe',
		});
	}
	// > magnificPopup function	by = magnific-popup.js =========================== //
	function magnific_popup(){
		jQuery('.mfp-gallery').magnificPopup({
		delegate: '.mfp-link',
		type: 'image',
		tLoading: 'Loading image #%curr%...',
		mainClass: 'mfp-img-mobile',
		gallery: {
			enabled: true,
			navigateByImgClick: true,
			preload: [0,1] // Will preload 0 - before current, and 1 after the current image
		},
		image: {
			tError: '<a href="%url%">The image #%curr%</a> could not be loaded.',
		}
	});
	}
// > Main menu sticky on top  when scroll down function by = custom.js ========== //		
	function sticky_header(){
		if(jQuery('.sticky-header').length){
			var sticky = new Waypoint.Sticky({
			  element: jQuery('.sticky-header')
			});
		}
	}
	// > Sidebar sticky  when scroll down function by = theia-sticky-sidebar.js ========== //		
	function sticky_sidebar(){		
		$('.rightSidebar')
			.theiaStickySidebar({
				additionalMarginTop: 100
			});		
	}
// > page scroll top on button click function by = custom.js ===================== //	
	function scroll_top(){
		jQuery("button.scroltop").on('click', function() {
			jQuery("html, body").animate({
				scrollTop: 0
			}, 1000);
			return false;
		});
		jQuery(window).on("scroll", function() {
			var scroll = jQuery(window).scrollTop();
			if (scroll > 900) {
				jQuery("button.scroltop").fadeIn(1000);
			} else {
				jQuery("button.scroltop").fadeOut(1000);
			}
		});
	}
	
	
// > accordion active calss function by = custom.js ========================= //	
	function accordion_active() {
		$('.acod-head a').on('click', function() {
			$('.acod-head').removeClass('acc-actives');
			$(this).parents('.acod-head').addClass('acc-actives');
			$('.acod-title').removeClass('acc-actives'); //just to make a visual sense
			$(this).parent().addClass('acc-actives'); //just to make a visual sense
			($(this).parents('.acod-head').attr('class'));
		 });
	}	
	// > Nav submenu show hide on mobile by = custom.js
	function mobile_nav(){
		jQuery(".sub-menu").parent('li').addClass('has-child');
		jQuery("<div class='fa fa-angle-right submenu-toogle'></div>").insertAfter(".has-child > a");
		jQuery('.has-child a+.submenu-toogle').on('click',function(ev) {
			jQuery(this).parent().siblings(".has-child ").children(".sub-menu").slideUp(500, function(){
				jQuery(this).parent().removeClass('nav-active');
			});
			jQuery(this).next(jQuery('.sub-menu')).slideToggle(500, function(){
				jQuery(this).parent().toggleClass('nav-active');
			});
			ev.stopPropagation();
		});
	
	}
	
	// Mobile side drawer function by = custom.js
	function mobile_side_drawer(){
		jQuery('#mobile-side-drawer').on('click', function () { 
			jQuery('.mobile-sider-drawer-menu').toggleClass('active');
		});
	}	
    
    // > TouchSpin box function by  = jquery.bootstrap-touchspin.js =============== // 
    function input_number_vertical_form(){	
	jQuery("input[name='demo_vertical2']").TouchSpin({
	  verticalbuttons: true
	});	
}		
//  Counter Section function by = counterup.min.js
	function counter_section(){
		jQuery('.counter').counterUp({
			delay: 10,
			time: 3000
		});	
	}	

	
			    
/*--------------------------------------------------------------------------------------------
	Window on load ALL FUNCTION START
---------------------------------------------------------------------------------------------*/
	
	// > masonry function function by = isotope.pkgd.min.js ************************************* //	
	function masonryBox() {
		if ( jQuery().isotope ) {      
			var $container = jQuery('.masonry-wrap');
				$container.isotope({
					itemSelector: '.masonry-item',
					transitionDuration: '1s',
					originLeft: true,
					stamp: '.stamp',
				});

			$container.imagesLoaded().progress( function() {
				$container.isotope('layout');
			});

			jQuery('.masonry-filter li').on('click',function() {                           
				var selector = jQuery(this).find("a").attr('data-filter');
				jQuery('.masonry-filter li').removeClass('active');
				jQuery(this).addClass('active');
				$container.isotope({ filter: selector });
				return false;
			});
		}
	}
	
// > page loader function by = custom.js ========================= //		
	function page_loader() {
		jQuery('.loading-area').fadeOut(1000);
	}
	

	
// > Price Range Slider function by = custom.js ========================= //		
	function price_range_slider() {
		jQuery("#ex2").slider({});
	}

	
	
/*--------------------------------------------------------------------------------------------
    Window on scroll ALL FUNCTION START
---------------------------------------------------------------------------------------------*/
    function color_fill_header() {
        var scroll = $(window).scrollTop();
        if(scroll >= 100) {
            $(".main-bar").addClass("color-fill");
        } else {
            (scroll = 100); $(".main-bar").removeClass("color-fill");
        }
    }

	
	
/*--------------------------------------------------------------------------------------------
	document.ready ALL FUNCTION START
---------------------------------------------------------------------------------------------*/
	jQuery(document).ready(function() {
		
		// Wow Animate function by = owl.js
    	wow_animate(),  
		// testimonial One Carousel Onefunction by = owl.js **************************************************
		aon_testi_one(), 
		// Case Studies Carousel Onefunction by = owl.js **************************************************
		aon_case_studies(), 
		// Lates Discover Carousel function by = owl.js **************************************************
    	aon_lates_discover(),   
		// Features CarouselCarousel function by = owl.js **************************************************
		aon_features_carousel(),   
        // Header Search Popup function by = custom.js ========================= //	
        header_search_popup(),           
		// > Video responsive function by = custom.js 
		video_responsive(),
	   // Banner Home 1 Full Width Slide function by = owl.carousel.js **************************************************************
		aon_bnr1_carousal(),
		// Banner Home 2 Full Width Slide function by = owl.carousel.js **************************************************************
		aon_bnr2_carousal(),
		// Banner Home 3 Full Width Slide function by = owl.carousel.js **********************
		aon_bnr3_carousal(),
		//  Service List function by = owl.js *********************************************************
		 mos_service_carousel(),
		//  Latest News Function by = owl.js *********************************************************
	     mos_news_carousel(),
		//  Our Expart Team Function by = owl.js *********************************************************
		mos_team_carousel(),  
		//  Our Expart Team 2 Function by = owl.js *********************************************************
		mos_team2_carousel(),
		//  Our Expart Team 3 Function by = owl.js ************************************************
		mos_team3_carousel(),    
		//  Our Solutions Function by = owl.js *********************************************************
		mos_solutions_carousel(), 
		 // > LIGHTBOX Gallery Popup function by = lc_lightbox.lite.js =========================== //      
		lightbox_popup(),
		// > magnificPopup for video function by = magnific-popup.js
		magnific_video(),
		// > magnificPopup function	by = magnific-popup.js =========================== //
		magnific_popup()
		// > Main menu sticky on top  when scroll down function by = custom.js		
		sticky_header(),
	    // > Sidebar sticky  when scroll down function by = theia-sticky-sidebar.js ========== //		
		sticky_sidebar(),
		// > page scroll top on button click function by = custom.js	
		scroll_top(),
        // > accordion active calss function by = custom.js ========================= //	
        accordion_active(),            
		// > Nav submenu on off function by = custome.js ===================//
		mobile_nav(),
		// Mobile side drawer function by = custom.js
		mobile_side_drawer(),
		// > TouchSpin box function by  = jquery.bootstrap-touchspin.js 
		input_number_vertical_form(),
		//  Counter Section function by = counterup.min.js
		counter_section(),
		// > Price Range Slider function by = custom.js ========================= //		
		price_range_slider()
			
	}); 	
/*--------------------------------------------------------------------------------------------
	Window Load START
---------------------------------------------------------------------------------------------*/
	jQuery(window).on('load', function () {
		// > page loader function by = custom.js		
		page_loader();
		// > Window on scroll header color fill 
		color_fill_header();
		// > masonry function function by = isotope.pkgd.min.js ************************************* //	
		masonryBox();
});
 /*===========================
	Window Scroll ALL FUNCTION START
===========================*/
	jQuery(window).on('scroll', function () {
	// > Window on scroll header color fill 
		color_fill_header();
	});
	
/*===========================
	Window Resize ALL FUNCTION START
===========================*/
	jQuery(window).on('resize', function () {
	});jQuery(window).resize();
	
	
})(window.jQuery);
