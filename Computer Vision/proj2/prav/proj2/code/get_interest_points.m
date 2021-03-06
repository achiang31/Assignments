% Local Feature Stencil Code
% CS 4476 / 6476: Computer Vision, Georgia Tech
% Written by James Hays

% Returns a set of interest points for the input image

% 'image' can be grayscale or color, your choice.
% 'feature_width', in pixels, is the local feature width. It might be
%   useful in this function in order to (a) suppress boundary interest
%   points (where a feature wouldn't fit entirely in the image, anyway)
%   or (b) scale the image filters being used. Or you can ignore it.

% 'x' and 'y' are nx1 vectors of x and y coordinates of interest points.
% 'confidence' is an nx1 vector indicating the strength of the interest
%   point. You might use this later or not.
% 'scale' and 'orientation' are nx1 vectors indicating the scale and
%   orientation of each interest point. These are OPTIONAL. By default you
%   do not need to make scale and orientation invariant local features.
function [x, y, confidence, scale, orientation] = get_interest_points(image, feature_width)

% Implement the Harris corner detector (See Szeliski 4.1.1) to start with.
% You can create additional interest point detector functions (e.g. MSER)
% for extra credit.

% If you're finding spurious interest point detections near the boundaries,
% it is safe to simply suppress the gradients / corners near the edges of
% the image.

% The lecture slides and textbook are a bit vague on how to do the
% non-maximum suppression once you've thresholded the cornerness score.
% You are free to experiment. Here are some helpful functions:
%  BWLABEL and the newer BWCONNCOMP will find connected components in 
% thresholded binary image. You could, for instance, take the maximum value
% within each component.
%  COLFILT can be used to run a max() operator on each sliding window. You
% could use this to ensure that every interest point is at a local maximum
% of cornerness.

% Placeholder that you can delete -- random points
% x = ceil(rand(500,1) * size(image,2));
% y = ceil(rand(500,1) * size(image,1));
alpha = .04;
filter = fspecial('gaussian', [3 3], .5);
image = imfilter(image,filter);
[Gx,Gy] = imgradientxy(image);
IX2 = Gx .* Gx;
IY2 = Gy .* Gy;


part1 = IX2.*IY2;
part2 = (IX2 .* IY2).* (IX2 .* IY2);
part3 = alpha * (IX2+IY2).*(IX2+IY2);

cornerness = part1 - part2 - part3;

filter2 = fspecial('gaussian', [9 9], .5);
cornerness = imfilter(cornerness,filter2);

xs = [];
ys = [];


%threshold is .06 for notre dame


xs1 = [];
ys1 = [];
for j=1:size(cornerness,1)
   for i=1:size(cornerness,2)
      if cornerness(j,i) > .06
         xs1 = [xs1; i];
         ys1 = [ys1; j];
      end
   end
end

x = xs1;
y = ys1;

 






